"""Slave (arm-mounted, follower) gripper assets.

The files ship in the ROS package ``taccap_slave_description``; in a pip install
they live under ``taccap_description/share/slave``.
"""

from taccap_description.share.slave import ASSET_ROOT

__all__ = ["ASSET_ROOT", "get_urdf_path", "get_xacro_path", "get_mjcf_path", "get_usd_path"]


def _suffix(with_mount):
    return "_with_mount" if with_mount else ""


def get_urdf_path(*, with_mount=False):
    """Portable URDF, optionally with the Asm_link flange adapter."""
    return ASSET_ROOT / "urdf" / f"taccap_g1_slave{_suffix(with_mount)}.urdf"


def get_xacro_path():
    """Prefixable macro; include it from an application Xacro."""
    return ASSET_ROOT / "urdf" / "taccap_g1_slave_macro.xacro"


def get_mjcf_path(*, with_mount=False):
    """MJCF model with the finger actuator and mimic equality."""
    return ASSET_ROOT / "mjcf" / f"taccap_g1_slave{_suffix(with_mount)}.xml"


def get_usd_path(*, with_mount=False):
    """Fixed-base USD with a PhysX mimic-joint constraint."""
    return ASSET_ROOT / "usd" / f"taccap_g1_slave{_suffix(with_mount)}.usda"
