"""Master (handheld, leader) gripper assets, one model per hand.

The files ship in the ROS package ``taccap_master_description``; in a pip
install they live under ``taccap_description/share/master``. Visual and
kinematic only: no inertia, collision or actuator.
"""

from taccap_description.share.master import ASSET_ROOT

__all__ = ["ASSET_ROOT", "get_urdf_path", "get_xacro_path", "get_mjcf_path", "get_usd_path"]

SIDES = ("left", "right")


def _side(side):
    if side not in SIDES:
        raise ValueError("Master gripper side must be 'left' or 'right'")
    return side


def get_urdf_path(*, side):
    """URDF of the left or right master."""
    return ASSET_ROOT / "urdf" / f"taccap_g1_master_{_side(side)}.urdf"


def get_xacro_path(*, side):
    """Prefixable macro; include it from an application Xacro."""
    return get_urdf_path(side=side).with_suffix(".urdf.xacro")


def get_mjcf_path(*, side):
    """Mocap-based visual model with no dynamic DOFs or contacts."""
    return ASSET_ROOT / "mjcf" / f"{_side(side)}.xml"


def get_usd_path(*, side, animated=False):
    """Visual-only USD, optionally with a 2-second open/close cycle."""
    suffix = "_open_close" if animated else ""
    return ASSET_ROOT / "usd" / f"{_side(side)}{suffix}.usda"
