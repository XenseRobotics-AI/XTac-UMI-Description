"""The imported STEP-derived geometry and measured physics remain traceable."""

import hashlib
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from taccap_description import ASSET_ROOT, get_urdf_path

REPOSITORY = Path(__file__).resolve().parents[1]
VENDOR = REPOSITORY / "vendor/taccap_slave"


def test_snapshot_and_shipped_meshes_match_upstream_lock():
    lock = json.loads((VENDOR / "upstream.json").read_text())
    assert json.loads((ASSET_ROOT / "config/upstream.json").read_text()) == lock
    actual = {
        str(p.relative_to(VENDOR / "source")): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (VENDOR / "source").rglob("*") if p.is_file()
    }
    assert actual == lock["files_sha256"]
    assert lock["path"].endswith("/slave-v2026.10.23")
    for relative, digest in actual.items():
        if relative.startswith("meshes/"):
            assert hashlib.sha256((ASSET_ROOT / relative).read_bytes()).hexdigest() == digest
    subprocess.run([sys.executable, str(REPOSITORY / "scripts/import_slave.py"), "--check"], check=True)


@pytest.mark.parametrize("with_mount", [False, True])
def test_six_part_model_mass_and_camera_com(with_mount):
    root = ET.parse(get_urdf_path(with_mount=with_mount)).getroot()
    masses = {link.get("name"): float(link.find("inertial/mass").get("value"))
              for link in root.findall("link") if link.find("inertial") is not None}
    expected = {"taccap_base_link": .153, "taccap_motor_link": .299,
                "taccap_left_finger_link": .140, "taccap_right_finger_link": .140,
                "taccap_camera_body_link": .018}
    if with_mount:
        expected["taccap_mount_link"] = .035
    assert masses == expected
    assert sum(masses.values()) == pytest.approx(.785 if with_mount else .750)
    camera = root.find("link[@name='taccap_camera_body_link']")
    com = [float(v) for v in camera.find("inertial/origin").get("xyz").split()]
    assert com == pytest.approx([-.02305604, .00009135, .06677412], abs=1e-14)
    for name in ("taccap_eef_link", "taccap_camera_link", "taccap_camera_optical_link"):
        assert not list(root.find(f"link[@name='{name}']"))
    base = root.find("link[@name='taccap_base_link']")
    assert base.find("visual/geometry/mesh").get("filename") == "../meshes/body_link.STL"
    assert base.find("collision/geometry/mesh").get("filename") == "../meshes/collision/body_link.stl"
    assert len(root.findall("joint[@name='taccap_mount_joint']")) == int(with_mount)


def test_commit_pin_accepts_exact_snapshot_and_rejects_changed_or_missing_files(tmp_path):
    """Exercise real Git commits in scratch repos, without changing either live repo."""
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    git = ["git", "-C", str(upstream), "-c", "init.defaultBranch=fixture",
           "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
           "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid"]
    subprocess.run(git + ["init", "-q"], check=True)
    lock = json.loads((VENDOR / "upstream.json").read_text())
    source = upstream / lock["path"]
    shutil.copytree(VENDOR / "source", source)

    def commit():
        subprocess.run(git + ["add", "."], check=True)
        subprocess.run(git + ["commit", "-qm", "fixture"], check=True)
        return subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()

    revision = commit()
    sandbox = tmp_path / "downstream"
    shutil.copytree(VENDOR, sandbox / "vendor/taccap_slave")
    (sandbox / "scripts").mkdir()
    importer = sandbox / "scripts/import_slave.py"
    shutil.copyfile(REPOSITORY / "scripts/import_slave.py", importer)

    def pin(sha):
        return subprocess.run([sys.executable, str(importer), "--source-repo",
                               str(upstream), "--pin-commit", sha], capture_output=True, text=True)

    assert pin(revision).returncode == 0
    pinned = sandbox / "vendor/taccap_slave/upstream.json"
    accepted = pinned.read_bytes()
    assert json.loads(accepted)["revision"] == revision
    assert (sandbox / "ros/taccap_description/config/upstream.json").read_bytes() == accepted
    (source / "README.md").write_text("changed source\n")
    rejected = pin(commit())
    assert rejected.returncode != 0 and "differs from snapshot" in rejected.stderr
    assert pinned.read_bytes() == accepted
    (source / "README.md").unlink()
    rejected = pin(commit())
    assert rejected.returncode != 0 and "file set differs" in rejected.stderr
    assert pinned.read_bytes() == accepted
