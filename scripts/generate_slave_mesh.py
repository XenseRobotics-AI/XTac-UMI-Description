"""Remove the embedded adapter from the slave base, retaining source STL bytes.

Match Asm_link triangles in the base frame using the Xacro mounting transform.
Only matched triangle records are removed; no remeshing or physical estimation.
"""

import argparse
import hashlib
import json
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import xacro
from _provenance import update_config
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

ASSETS = Path(__file__).resolve().parents[1] / "ros/taccap_description"
OUTPUT = "base_link.STL"
TOLERANCE_M = 1e-7
DTYPE = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attr", "<u2")])


def read_stl(path):
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + count * 50:
        raise ValueError(f"Expected binary STL: {path}")
    return data, np.frombuffer(data, dtype=DTYPE, offset=84, count=count)


def pose(origin):
    result = np.eye(4)
    result[:3, 3] = np.fromstring(origin.get("xyz"), sep=" ")
    result[:3, :3] = Rotation.from_euler(
        "xyz", np.fromstring(origin.get("rpy"), sep=" ")
    ).as_matrix()
    return result


def generate(check=False):
    metadata = json.loads((ASSETS / "config/model.json").read_text())
    source, base = read_stl(ASSETS / "meshes/base_link_with_mount.STL")
    adapter_bytes, adapter = read_stl(ASSETS / "meshes/Asm_link.STL")
    for name, data in [
        ("base_link_with_mount.STL", source),
        ("Asm_link.STL", adapter_bytes),
    ]:
        if hashlib.sha256(data).hexdigest() != metadata["mesh_sha256"][name]:
            raise ValueError(f"Source mesh hash changed: {name}")
    # Asm_link.STL and base_link_with_mount.STL share the native CAD axes;
    # compose the mounted placements of both meshes to relate them.
    urdf = ET.fromstring(
        xacro.process_file(
            str(ASSETS / "urdf/taccap_g1_slave.urdf.xacro"),
            mappings={"with_mount": "true", "mesh_root": "../meshes"},
        ).toxml()
    )
    mount_to_base = pose(urdf.find("joint[@name='taccap_mount_joint']/origin"))
    adapter_mesh = pose(urdf.find("link[@name='taccap_mount_link']/visual/origin"))
    base_mesh = mount_to_base @ pose(
        urdf.find("link[@name='taccap_base_link']/visual/origin")
    )
    adapter_to_base = np.linalg.inv(adapter_mesh) @ base_mesh
    translation = adapter_to_base[:3, 3].round(12) + 0.0
    rotation = Rotation.from_matrix(adapter_to_base[:3, :3])
    rpy = rotation.as_euler("xyz").round(12) + 0.0
    # The transform maps base coordinates to adapter coordinates; invert it.
    vertices = rotation.inv().apply(
        adapter["vertices"].astype(float).reshape(-1, 3) - translation
    )
    unique, inverse = np.unique(
        base["vertices"].reshape(-1, 3), axis=0, return_inverse=True
    )
    distances, indices = cKDTree(unique).query(vertices)
    if distances.max() > TOLERANCE_M:
        raise ValueError("Adapter does not match the source base within tolerance")
    face_lookup = {}
    for index, triangle in enumerate(inverse.reshape(-1, 3)):
        key = tuple(sorted(triangle))
        face_lookup.setdefault(key, []).append(index)
    removed = []
    for triangle in indices.reshape(-1, 3):
        matches = face_lookup.get(tuple(sorted(triangle)), [])
        if len(matches) != 1:
            raise ValueError("Adapter triangle must match exactly one base triangle")
        removed.append(matches[0])
    if len(set(removed)) != len(adapter):
        raise ValueError("Adapter triangle mapping is not one-to-one")
    keep = np.ones(len(base), dtype=bool)
    keep[removed] = False
    result = source[:80] + struct.pack("<I", int(keep.sum())) + base[keep].tobytes()
    target = ASSETS / "meshes" / OUTPUT
    provenance = {
        OUTPUT: {
            "generator": "scripts/generate_slave_mesh.py",
            "operation": "Remove only triangles matching Asm_link.STL in the base frame; retain all other binary STL triangle records in source order.",
            "source": "base_link_with_mount.STL",
            "source_original_filename": "base_link.STL",
            "source_sha256": metadata["mesh_sha256"]["base_link_with_mount.STL"],
            "removed_component": "Asm_link.STL",
            "removed_component_sha256": metadata["mesh_sha256"]["Asm_link.STL"],
            "transform_source": "urdf/taccap_g1_slave_macro.xacro with_mount: inverse(asm_visual origin) * taccap_mount_joint * base_visual origin, inverted",
            "adapter_to_base_joint_xyz_m": translation.tolist(),
            "adapter_to_base_joint_rpy_rad": rpy.tolist(),
            "vertex_match_tolerance_m": TOLERANCE_M,
            "source_triangles": len(base),
            "removed_triangles": len(removed),
            "output_triangles": int(keep.sum()),
            "sha256": hashlib.sha256(result).hexdigest(),
            "physics": "Existing mass/inertia retained without re-identification; collision mesh geometry changes with the visual mesh. No contact calibration.",
        }
    }
    if check:
        if not target.is_file() or target.read_bytes() != result:
            raise SystemExit(f"Regenerate stale mesh: {target}")
    else:
        target.write_bytes(result)
    update_config(ASSETS / "config/model.json", "derived_meshes", provenance, check)
    print(target.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    generate(parser.parse_args().check)
