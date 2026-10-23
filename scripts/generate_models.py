"""Generate current TacCap URDF and MJCF variants from the slave Xacro.

This converter supports the mesh-only fixed/revolute TacCap model in this
repository. It is not a general URDF importer. Generated files are checked in
so consumers need neither Xacro nor SciPy.
"""

import argparse
import copy
import xml.etree.ElementTree as ET
from pathlib import Path

import xacro
from scipy.spatial.transform import Rotation

ASSETS = Path(__file__).resolve().parents[1] / "ros" / "taccap_description"


def mesh_name(filename):
    relative = Path(filename).relative_to("../meshes")
    return "taccap_" + "_".join(relative.with_suffix("").parts) + "_mesh"


def pose(origin):
    if origin is None:
        return {}
    result = {"pos": origin.get("xyz", "0 0 0")}
    quaternion = Rotation.from_euler(
        "xyz", [float(v) for v in origin.get("rpy", "0 0 0").split()]
    ).as_quat()
    result["quat"] = " ".join(f"{v:.16g}" for v in quaternion[[3, 0, 1, 2]])
    return result


def make_mjcf(urdf):
    model = ET.parse(ASSETS / "config" / "mujoco.xml").getroot()
    model.set("model", urdf.get("name"))
    patches = model.find("worldbody")
    model.remove(patches)
    assets = ET.SubElement(model, "asset")
    for material in urdf.findall("material"):
        ET.SubElement(
            assets,
            "material",
            name=material.get("name"),
            rgba=material.find("color").get("rgba"),
        )
    referenced_meshes = sorted({mesh.get("filename") for mesh in urdf.findall(".//mesh")})
    for filename in referenced_meshes:
        ET.SubElement(assets, "mesh", name=mesh_name(filename), file=filename)

    links = {link.get("name"): link for link in urdf.findall("link")}
    children = {}
    parents = {}
    for joint in urdf.findall("joint"):
        child = joint.find("child").get("link")
        parents[child] = joint
        children.setdefault(joint.find("parent").get("link"), []).append(child)
    roots = set(links) - set(parents)
    if len(roots) != 1:
        raise ValueError(f"Expected one TacCap root, found {roots}")
    worldbody = ET.SubElement(model, "worldbody")

    def add_body(name, parent):
        link = links[name]
        joint = parents.get(name)
        body = ET.SubElement(parent, "body", name=name)
        if joint is not None:
            body.attrib.update(pose(joint.find("origin")))
        inertial = link.find("inertial")
        if inertial is not None:
            values = inertial.find("inertia").attrib
            attributes = pose(inertial.find("origin"))
            # All source inertia frames are aligned with their link frame.
            if attributes.pop("quat") != "1 0 0 0":
                raise ValueError(
                    "Rotated inertia frames are not supported by this TacCap converter"
                )
            attributes["mass"] = inertial.find("mass").get("value")
            off_diagonal = [values[key] for key in ("ixy", "ixz", "iyz")]
            key = (
                "diaginertia"
                if all(float(v) == 0 for v in off_diagonal)
                else "fullinertia"
            )
            order = (
                ("ixx", "iyy", "izz")
                if key == "diaginertia"
                else ("ixx", "iyy", "izz", "ixy", "ixz", "iyz")
            )
            attributes[key] = " ".join(values[k] for k in order)
            ET.SubElement(body, "inertial", attributes)
        if joint is not None and joint.get("type") != "fixed":
            if joint.get("type") != "revolute":
                raise ValueError("Only fixed and revolute TacCap joints are supported")
            limit = joint.find("limit")
            dynamics = joint.find("dynamics")
            ET.SubElement(
                body,
                "joint",
                name=joint.get("name"),
                type="hinge",
                axis=joint.find("axis").get("xyz"),
                range=f"{limit.get('lower')} {limit.get('upper')}",
                damping=dynamics.get("damping"),
                frictionloss=dynamics.get("friction"),
            )
        for geometry in link:
            if geometry.tag not in ("visual", "collision"):
                continue
            mesh = geometry.find("geometry/mesh")
            if mesh is None:
                raise ValueError("The TacCap source must use mesh geometry")
            attributes = {
                "name": geometry.get("name"),
                "type": "mesh",
                "mass": "0",
                "mesh": mesh_name(mesh.get("filename")),
            }
            attributes.update(pose(geometry.find("origin")))
            if geometry.tag == "visual":
                attributes.update(
                    group="1",
                    contype="0",
                    conaffinity="0",
                    material=geometry.find("material").get("name"),
                )
            else:
                attributes["group"] = "0"
            ET.SubElement(body, "geom", attributes)
        for child in children.get(name, []):
            add_body(child, body)

    root_name = roots.pop()
    add_body(root_name, worldbody)
    ET.SubElement(
        worldbody.find("body"),
        "site",
        name="ft_frame",
        pos="0 0 0",
        size="0.005",
        rgba="1 0 0 0",
        group="1",
    )
    for patch in patches:
        body = worldbody.find(f".//body[@name='{patch.get('name')}']")
        if body is None and patch.get("name") == "taccap_mount_link":
            continue  # Optional mounting adapter.
        if body is None:
            raise ValueError(f"No body for MuJoCo patch: {patch.get('name')}")
        for element in patch:
            if element.tag == "site":
                body.append(copy.deepcopy(element))
            else:
                target = body.find(f"{element.tag}[@name='{element.get('name')}']")
                if target is None:
                    raise ValueError(f"No target for MuJoCo patch: {element.attrib}")
                target.attrib.update(element.attrib)
    # The actuator force limit is the finger motor's output torque (URDF effort).
    for actuator in model.find("actuator"):
        effort = urdf.find(f"joint[@name='{actuator.get('joint')}']/limit").get("effort")
        actuator.set("forcerange", f"-{effort} {effort}")
    equality = ET.SubElement(model, "equality")
    for joint in urdf.findall("joint"):
        mimic = joint.find("mimic")
        if mimic is not None:
            ET.SubElement(
                equality,
                "joint",
                name="left_follows_right",
                joint1=joint.get("name"),
                joint2=mimic.get("joint"),
                polycoef=f"{mimic.get('offset', '0')} {mimic.get('multiplier', '1')} 0 0 0",
                solref="0.002 1",
            )
    return model


def generated_files(urdf_only=False):
    for with_mount in (False, True):
        suffix = "_with_mount" if with_mount else ""
        document = xacro.process_file(
            str(ASSETS / "urdf" / "taccap_g1_slave.urdf.xacro"),
            mappings={"with_mount": str(with_mount).lower(), "mesh_root": "../meshes"},
        )
        urdf = ET.fromstring(document.toxml())
        urdf.set("name", f"taccap_g1_slave{suffix}")
        outputs = [("urdf", "urdf", urdf)]
        if not urdf_only:
            outputs.append(("mjcf", "xml", make_mjcf(copy.deepcopy(urdf))))
        for directory, extension, root in outputs:
            root.insert(
                0,
                ET.Comment(
                    " Generated by scripts/generate_models.py; edit Xacro/config sources instead. "
                ),
            )
            ET.indent(root, space="  ")
            yield (
                ASSETS / directory / f"taccap_g1_slave{suffix}.{extension}",
                ET.tostring(root, encoding="unicode") + "\n",
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if checked-in models differ from generated output",
    )
    parser.add_argument("--urdf-only", action="store_true", help="Update URDF only, leaving MJCF untouched")
    args = parser.parse_args()
    for path, content in generated_files(urdf_only=args.urdf_only):
        if args.check:
            if not path.is_file() or path.read_text() != content:
                raise SystemExit(f"Regenerate stale model: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        print(path.name)


if __name__ == "__main__":
    main()
