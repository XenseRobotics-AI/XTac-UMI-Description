"""Visual appearance shared by the slave and master USD generators.

The reference is the xensim-bench TacCap asset (``Looks/TacCap/*``), which
matches the physical gripper: silver structure, light-grey finger covers, black
frame, **yellow fingertips and lens cap**, a dark gel pad and a darker lens.

URDF ``<color>`` carries one flat colour per visual and no PBR parameters, so the
materials are defined once here and both generators author them as
``UsdPreviewSurface`` shaders. The finer per-face split (yellow fingertips, lens
cap and gel on meshes that are mostly silver or black) comes from
``ros/taccap_description/config/appearance.json``, produced by
``scripts/extract_appearance_partition.py``.
"""

import json
from pathlib import Path

import numpy as np
from pxr import Gf, Sdf, UsdGeom, UsdShade, Vt

# ``rgba`` is the URDF/sRGB value; ``metallic``/``roughness`` the PBR pair.
MATERIALS = {
    "taccap_silver": dict(rgba=(0.58, 0.60, 0.62, 1.0), metallic=0.50, roughness=0.35),
    "taccap_cover": dict(rgba=(0.65, 0.70, 0.71, 1.0), metallic=0.00, roughness=0.60),
    "taccap_black": dict(rgba=(0.018, 0.020, 0.022, 1.0), metallic=0.05, roughness=0.70),
    "taccap_yellow": dict(rgba=(0.95, 0.75, 0.012, 1.0), metallic=0.00, roughness=0.48),
    "taccap_gel": dict(rgba=(0.055, 0.055, 0.055, 1.0), metallic=0.00, roughness=0.85),
    "taccap_lens": dict(rgba=(0.004, 0.004, 0.004, 1.0), metallic=0.10, roughness=0.12),
}

PARTITION = Path(__file__).resolve().parents[1] / "ros/taccap_description/config/appearance.json"

# URDF material name -> appearance material. The gripper URDFs use the appearance
# names directly; the aliases are kept so older firmware-facing names still map.
URDF_MATERIAL_OF = {
    **{name: name for name in MATERIALS},
    "taccap_base_mat": "taccap_silver",
    "taccap_left_mat": "taccap_yellow",
    "taccap_right_mat": "taccap_yellow",
    "taccap_mount_mat": "taccap_cover",
    "left_shell": "taccap_silver",
    "right_shell": "taccap_silver",
    "left_finger": "taccap_yellow",
    "right_finger": "taccap_yellow",
}


def urdf_material(name):
    """Map a URDF ``<material name=...>`` onto an appearance material.

    The masters side-qualify their materials (``left_silver``) so both sides can
    be combined in one xacro without clashing; the trailing part names the
    appearance material.
    """
    if name in URDF_MATERIAL_OF:
        return URDF_MATERIAL_OF[name]
    for prefix in ("left_", "right_"):
        if name.startswith(prefix):
            rest = name[len(prefix):]
            if rest in MATERIALS:
                return rest
            if "taccap_" + rest in MATERIALS:
                return "taccap_" + rest
    raise KeyError(f"No appearance material for URDF material {name!r}")


def define_materials(stage, root):
    """Author one ``UsdPreviewSurface`` per entry of :data:`MATERIALS`."""
    UsdGeom.Scope.Define(stage, root + "/Looks")
    materials = {}
    for name, spec in MATERIALS.items():
        material = UsdShade.Material.Define(stage, f"{root}/Looks/{name}")
        shader = UsdShade.Shader.Define(stage, f"{root}/Looks/{name}/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
            Gf.Vec3f(*spec["rgba"][:3])
        )
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(spec["metallic"])
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(spec["roughness"])
        shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(spec["rgba"][3])
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        materials[name] = material
    return materials


def face_partition():
    """``{package-relative mesh path: {"faces": n, "subsets": {material: faces}}}``.

    Keyed by the shipped path (``slave/base_link.STL``) rather than the stem: the
    master's ``base_link.STL`` is a different part that happens to share the name,
    and applying the slave's partition to it would paint the wrong triangles.
    """
    if not PARTITION.is_file():
        return {}
    data = json.loads(PARTITION.read_text())["partition"]
    result = {}
    for relative, entry in data.items():
        order = entry["order"]
        labels = []
        runs = entry["runs"]
        for i in range(0, len(runs), 2):
            labels.extend([order[runs[i + 1]]] * runs[i])
        if len(labels) != entry["faces"]:
            raise ValueError(
                f"{relative}: partition covers {len(labels)} of {entry['faces']} faces"
            )
        indices = {}
        for index, name in enumerate(labels):
            indices.setdefault(name, []).append(index)
        result[relative] = {"faces": entry["faces"], "subsets": indices}
    return result


def partition_for(partitions, relative, face_count):
    """The subsets for one mesh, or ``None`` when it has no partition.

    A face-count mismatch means the partition was built for a different mesh and
    would paint arbitrary triangles, so it is refused instead of applied.
    """
    entry = partitions.get(relative)
    if entry is None:
        return None
    if entry["faces"] != face_count:
        raise ValueError(
            f"{relative}: partition has {entry['faces']} faces but the mesh has "
            f"{face_count}; regenerate appearance.json for this mesh"
        )
    return entry["subsets"]


def bind_face_materials(mesh, materials, subsets):
    """Split ``mesh`` into one ``GeomSubset`` per material (per-face colours)."""
    for name, faces in subsets.items():
        if name not in materials:
            continue
        subset = UsdGeom.Subset.CreateGeomSubset(
            mesh,
            name,
            UsdGeom.Tokens.face,
            Vt.IntArray.FromNumpy(np.asarray(faces, dtype=np.int32)),
            "materialBind",
        )
        UsdShade.MaterialBindingAPI.Apply(subset.GetPrim()).Bind(materials[name])
