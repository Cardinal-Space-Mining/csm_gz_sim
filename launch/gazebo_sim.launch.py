import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch.actions import AppendEnvironmentVariable
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    pkg_path = get_package_share_directory('csm_gz_sim')
    ros_gz_sim_pkg_path = get_package_share_directory('ros_gz_sim')

    lance_model_path = os.path.join( pkg_path, 'description', 'lance', 'model.sdf' )
    bridge_params = os.path.join( pkg_path, 'config', 'ros_gz_bridge.yaml' )

    worlds_dir = os.path.join( pkg_path, 'worlds' )
    artemis_arena_world = os.path.join( worlds_dir, 'artemis-arena.world' )
    maze_world = os.path.join( worlds_dir, 'maze.world' )
    bridge_world = os.path.join( worlds_dir, 'arch-arena.world' )

    world_dict = {
        'arena' : artemis_arena_world,
        'maze' : maze_world,
        'bridge' : bridge_world
    }


    # set env vars
    append_gz_env_vars = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.join(pkg_path, 'description')
    )
    # launch gazebo server with the arena SDF
    launch_gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_pkg_path, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments = {
            'gz_args': ['-r -s -v4 ', world_dict['arena']],
            'on_exit_shutdown': 'true',
            'pause': 'true'
        }.items()
    )
    # start gazebo client
    launch_gz_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_pkg_path, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments = {'gz_args': '-g -v4 '}.items(),
        condition = IfCondition(LaunchConfiguration('gz_gui', default='true'))
    )
    # spawn the robot
    launch_robot_spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'lance',
            '-file', lance_model_path,
            '-x', '1.0',
            '-y', '1.0',
            '-z', '0.0'
        ],
        output='screen'
    )
    # run topic bridge
    launch_ros_gz_topic_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={ bridge_params }',
        ],
        output='screen'
    )
    # run image transport bridge
    launch_ros_gz_image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=[
            # '/model/lance/fwd_cam/image',
            # '/model/lance/rght_cam/image',
            # '/model/lance/left_cam/image',
            '/arena/cam1/image'
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('gz_gui', default_value='false'),
        DeclareLaunchArgument('gz_map', default_value='arena'),
        append_gz_env_vars,
        launch_gz_server,
        launch_gz_client,
        launch_robot_spawn,
        launch_ros_gz_topic_bridge,
        launch_ros_gz_image_bridge
    ])
