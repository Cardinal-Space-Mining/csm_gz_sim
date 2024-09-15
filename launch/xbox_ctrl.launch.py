import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    pkg_path = get_package_share_directory('csm_gz_sim')

    # joystick publisher
    launch_joy_pub = Node(
        package = 'joy',
        executable = 'joy_node',
        parameters = [
            os.path.join( pkg_path, 'config', 'xbox_ctrl.yaml' ),
            { 'use_sim_time' : True }
        ]
    )
    # target state publisher
    launch_drive_teleop = Node(
        name = 'teleop_node',
        package = 'teleop_twist_joy',
        executable = 'teleop_node',
        output = 'screen',
        parameters = [
            os.path.join( pkg_path, 'config', 'xbox_ctrl.yaml' ),
            { 'use_sim_time' : True }
        ],
        remappings = [('/cmd_vel', '/robot_cmd_vel')]
    )

    return LaunchDescription([
        launch_joy_pub,
        launch_drive_teleop
    ])
