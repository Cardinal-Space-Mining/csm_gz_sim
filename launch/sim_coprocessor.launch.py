import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch_ros.actions import Node


def generate_launch_description():

    pkg_path = get_package_share_directory('lance_sim')

    launch_file_dir = os.path.join( pkg_path, 'launch' )


    # publish robot state to /tf
    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_file_dir, 'robot_state_publisher.launch.py')
        ),
        launch_arguments = {'use_sim_time': 'true'}.items()
    )
    # foxglove
    foxglove_node = Node(
        name = 'foxglove',
        package = 'foxglove_bridge',
        executable = 'foxglove_bridge',
        output = 'screen',
        condition = IfCondition( LaunchConfiguration('foxglove', default='true') ),
        parameters = [os.path.join(pkg_path, 'config', 'foxglove_bridge.yaml'), {'use_sim_time': True}]
    )

    return LaunchDescription([
        DeclareLaunchArgument('foxglove', default_value='true'),
        robot_state_publisher_cmd,
        foxglove_node
    ])