"""TacCap master visual/kinematic assets; no physics dependency required."""

from taccap_master_description.share import ASSET_ROOT


def get_master_urdf_path(*, side):
    """Return the explicitly selected left or right master gripper URDF."""
    if side not in ("left", "right"):
        raise ValueError("Master gripper side must be 'left' or 'right'")
    return ASSET_ROOT / "urdf" / f"taccap_g1_master_{side}.urdf"


def get_master_xacro_path(*, side):
    """Return the prefixable master macro (include it in an application Xacro)."""
    return get_master_urdf_path(side=side).with_suffix(".urdf.xacro")


def get_master_mjcf_path(*, side):
    """Return a mocap-based visual model with no dynamic DOFs or contacts."""
    get_master_urdf_path(side=side)  # Validate the side; MJCF/USD keep short filenames.
    return ASSET_ROOT / "mjcf" / f"{side}.xml"


def get_master_usd_path(*, side, animated=False):
    """Return a visual-only USD asset, optionally with a 2-second opening cycle."""
    get_master_urdf_path(side=side)  # Validate the side; MJCF/USD keep short filenames.
    suffix = "_open_close" if animated else ""
    return ASSET_ROOT / "usd" / f"{side}{suffix}.usda"
