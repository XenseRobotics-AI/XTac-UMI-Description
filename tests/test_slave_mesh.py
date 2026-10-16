"""Geometry regression: the base mesh is the original body mesh minus exactly the adapter."""

import struct
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial import cKDTree

from taccap_description import ASSET_ROOT, get_mjcf_path, get_urdf_path


# The original body mesh with the adapter embedded, kept only as a regression reference.
ORIGINAL_BASE = Path(__file__).resolve().parent / "data" / "slave" / "base_link_with_mount.STL"


def records(name):
    path = ORIGINAL_BASE if name == ORIGINAL_BASE.name else ASSET_ROOT / "meshes" / name
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    assert len(data) == 84 + 50 * count
    return [data[i : i + 50] for i in range(84, len(data), 50)]


def vertices(facets):
    return np.array([struct.unpack_from("<9f", f, 12) for f in facets]).reshape(
        -1, 3, 3
    )


def test_derived_base_removes_only_the_adapter():
    # Only the derived base ships; the original is a test reference.
    assert not (ASSET_ROOT / "meshes/base_link_with_mount.STL").exists()
    original = records("base_link_with_mount.STL")
    derived = records("base_link.STL")
    remaining = Counter(derived)
    removed = []
    # Verify surviving records occur in exactly their original sequence.
    retained = []
    for record in original:
        if remaining[record]:
            remaining[record] -= 1
            retained.append(record)
        else:
            removed.append(record)
    assert not +remaining
    assert retained == derived
    assert len(original) == 71396
    assert len(derived) == 69846
    assert len(removed) == len(records("Asm_link.STL")) == 1550
    adapter = vertices(records("Asm_link.STL")) + [-0.046023, 0.0060769, 0.01975]
    removed_vertices = vertices(removed)
    # Every removed face corresponds to exactly one adapter face, including
    # all three vertices; centroid proximity alone would be insufficient.
    distances, indices = cKDTree(removed_vertices.mean(axis=1)).query(
        adapter.mean(axis=1)
    )
    assert max(distances) < 1e-7
    assert len(set(indices)) == 1550
    for expected, actual in zip(adapter, removed_vertices[indices]):
        d = np.linalg.norm(expected[:, None] - actual[None], axis=2)
        assert np.all(d.min(axis=1) < 1e-7)
    # The adapter's rear-most surface cannot survive in the derived base.
    assert vertices(derived)[:, :, 0].min() > adapter[:, :, 0].min() + 0.003


@pytest.mark.parametrize("with_mount", [False, True])
def test_entry_points_use_derived_base_and_optional_adapter(with_mount):
    root = ET.parse(get_urdf_path(with_mount=with_mount)).getroot()
    base = root.find("link[@name='taccap_base_link']")
    for kind in ("visual", "collision"):
        assert (
            base.find(f"{kind}/geometry/mesh").get("filename")
            == "../meshes/base_link.STL"
        )
    mount = root.find("link[@name='taccap_mount_link']")
    assert (mount is not None) == with_mount
    if with_mount:
        assert len(mount.findall("visual")) == len(mount.findall("collision")) == 1
    assert len(root.findall("joint[@name='taccap_mount_joint']")) == int(with_mount)
    mjcf = ET.parse(get_mjcf_path(with_mount=with_mount)).getroot()
    assert (
        mjcf.find("asset/mesh[@name='taccap_base_mesh']").get("file")
        == "../meshes/base_link.STL"
    )
    assert len(mjcf.findall("asset/mesh[@name='taccap_asm_mesh']")) == int(with_mount)
