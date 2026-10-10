"""Show a TacCap master gripper in RViz with an interactive joint slider.

taccap_g1_master_left.urdf.xacro and taccap_g1_master_right.urdf.xacro define macros rather than robots, so this
launch expands the hand-written display_{side}.urdf.xacro wrappers, whose
mesh_root defaults to package://taccap_master_description. These are
visual/kinematic models: they carry no mass, inertia or collision data.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def launch_setup(context):
    share = get_package_share_directory("taccap_master_description")
    side = LaunchConfiguration("side").perform(context)
    prefix = LaunchConfiguration("prefix").perform(context)
    use_sim_time = LaunchConfiguration("use_sim_time")

    xacro_file = os.path.join(share, "urdf", f"display_{side}.urdf.xacro")
    command = ["xacro ", xacro_file]
    if prefix:
        command += [" prefix:=", prefix]

    robot_description = ParameterValue(Command(command), value_type=str)

    return [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[
                {"use_sim_time": use_sim_time, "robot_description": robot_description}
            ],
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", os.path.join(share, "rviz", f"{side}.rviz")],
        ),
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "side",
                default_value="left",
                choices=["left", "right"],
                description="Which master gripper to display",
            ),
            DeclareLaunchArgument(
                "prefix",
                default_value="",
                description="Prefix applied to links, joints and materials",
            ),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            OpaqueFunction(function=launch_setup),
        ]
    )
