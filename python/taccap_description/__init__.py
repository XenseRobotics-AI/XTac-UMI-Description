"""Resource paths for the XTac-UMI G1 (TacCap) gripper descriptions.

Importing this package needs no robotics framework.

    from taccap_description import slave, master
    slave.get_urdf_path(with_mount=True)
    master.get_urdf_path(side="left")
"""

from taccap_description import master, slave

__version__ = "0.2.0"
__all__ = ["master", "slave", "__version__"]
