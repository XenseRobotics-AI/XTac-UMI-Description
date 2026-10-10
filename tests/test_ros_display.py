"""Static checks for the ROS 2 display entry points.

No ROS is available here, so these verify what can be verified offline: the
launch files parse, the RViz presets are valid YAML, and every frame and file
they name exists in the model they display. Running `ros2 launch` remains a
manual step on a machine with ROS 2.
"""

import ast
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import xacro
import yaml

from taccap_description import ASSET_ROOT as SLAVE_ROOT
from taccap_master_description import ASSET_ROOT as MASTER_ROOT

# launch/ and rviz/ install into the ROS share and ship in the sdist, but are
# excluded from the Python wheel, so they are absent from ASSET_ROOT under a
# non-editable install. Read them from the repository instead, like the
# generator regressions do.
REPOSITORY = Path(__file__).resolve().parents[1]
SLAVE_SOURCE = REPOSITORY / "ros" / "taccap_description"
MASTER_SOURCE = REPOSITORY / "ros" / "taccap_master_description"

LAUNCH_FILES = [
    SLAVE_SOURCE / "launch" / "display.launch.py",
    MASTER_SOURCE / "launch" / "display.launch.py",
]
PRESETS = [
    (SLAVE_SOURCE / "rviz" / "taccap_g1_slave.rviz", "taccap_base_link"),
    (MASTER_SOURCE / "rviz" / "left.rviz", "left_base_link"),
    (MASTER_SOURCE / "rviz" / "right.rviz", "right_base_link"),
]


@pytest.mark.parametrize("path", LAUNCH_FILES, ids=lambda p: p.parents[2].name)
def test_launch_file_parses_and_declares_entry_point(path):
    module = ast.parse(path.read_text())
    functions = {
        node.name for node in module.body if isinstance(node, ast.FunctionDef)
    }
    assert {"launch_setup", "generate_launch_description"} <= functions


@pytest.mark.parametrize("path,frame", PRESETS, ids=lambda value: str(value)[-40:])
def test_rviz_preset_is_valid_and_targets_a_real_frame(path, frame):
    preset = yaml.safe_load(path.read_text())
    manager = preset["Visualization Manager"]
    assert manager["Global Options"]["Fixed Frame"] == frame
    classes = {display["Class"] for display in manager["Displays"]}
    assert "rviz_default_plugins/RobotModel" in classes
    model = next(
        display
        for display in manager["Displays"]
        if display["Class"] == "rviz_default_plugins/RobotModel"
    )
    assert model["Description Topic"]["Value"] == "robot_description"


def links(document):
    return {link.get("name") for link in document.findall("link")}


def test_slave_rviz_frame_exists_in_both_variants():
    _, frame = PRESETS[0]
    for with_mount in ("false", "true"):
        document = ET.fromstring(
            xacro.process_file(
                str(SLAVE_ROOT / "urdf" / "taccap_g1_slave.urdf.xacro"),
                mappings={"with_mount": with_mount},
            ).toxml()
        )
        assert frame in links(document)


@pytest.mark.parametrize("side", ("left", "right"))
def test_master_display_wrapper_is_standalone_and_uses_package_meshes(side):
    document = ET.fromstring(
        xacro.process_file(
            str(MASTER_ROOT / "urdf" / f"display_{side}.urdf.xacro")
        ).toxml()
    )
    assert document.get("name") == f"taccap_master_{side}"
    # The RViz preset for this side fixes on base_link.
    assert f"{side}_base_link" in links(document)
    meshes = {mesh.get("filename") for mesh in document.findall(".//mesh")}
    assert meshes
    for filename in meshes:
        assert filename.startswith(
            f"package://taccap_master_description/meshes/{side}/"
        )


@pytest.mark.parametrize("side", ("left", "right"))
def test_master_display_wrapper_accepts_a_prefix(side):
    document = ET.fromstring(
        xacro.process_file(
            str(MASTER_ROOT / "urdf" / f"display_{side}.urdf.xacro"),
            mappings={"prefix": "arm_"},
        ).toxml()
    )
    assert all(name.startswith("arm_") for name in links(document))
