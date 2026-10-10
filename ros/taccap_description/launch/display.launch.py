"""Show the TacCap G1 slave in RViz with an interactive joint slider.

The checked-in plain URDFs keep relative mesh paths, so this launch expands the
Xacro entry point instead: its mesh_root defaults to package://taccap_description.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def launch_setup(context):
    share = get_package_share_directory("taccap_description")
    xacro_file = os.path.join(share, "urdf", "taccap_g1_slave.urdf.xacro")

    with_mount = LaunchConfiguration("with_mount").perform(context)
    prefix = LaunchConfiguration("prefix").perform(context)
    use_sim_time = LaunchConfiguration("use_sim_time")

    command = ["xacro ", xacro_file, " with_mount:=", with_mount]
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
            arguments=["-d", os.path.join(share, "rviz", "taccap_g1_slave.rviz")],
        ),
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "with_mount",
                default_value="false",
                choices=["true", "false"],
                description="Load the Asm_link mounting-adapter variant",
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
