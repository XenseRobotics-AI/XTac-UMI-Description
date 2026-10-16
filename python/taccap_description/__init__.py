"""File paths for TacCap assets; importing this package needs no robotics framework."""

from taccap_description.share import ASSET_ROOT

__version__ = "0.1.1"


def get_urdf_path(*, with_mount=False):
    """Return a portable URDF, optionally including the Asm_link adapter."""
    suffix = "_with_mount" if with_mount else ""
    return ASSET_ROOT / "urdf" / f"taccap_g1_slave{suffix}.urdf"


def get_mjcf_path(*, with_mount=False):
    """Return an MJCF model, optionally including the Asm_link adapter."""
    suffix = "_with_mount" if with_mount else ""
    return ASSET_ROOT / "mjcf" / f"taccap_g1_slave{suffix}.xml"


def get_usd_path(*, with_mount=False):
    """Return a fixed-base USD asset with a PhysX mimic-joint constraint."""
    suffix = "_with_mount" if with_mount else ""
    return ASSET_ROOT / "usd" / f"taccap_g1_slave{suffix}.usda"
