#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument
from launch.actions import LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    
    # Slam toolbox launch setup
   

    namespace=LaunchConfiguration('namespace')
    declare_namespace=DeclareLaunchArgument('namespace',
                                            default_value='master',
                                            description='Namespace for slam node')
    
    ekf_params_file=LaunchConfiguration('ekf_params_file')
    declare_ekf_params_file_cmd=DeclareLaunchArgument('ekf_params_file',
                    default_value=os.path.join(get_package_share_directory("rover_bringup"),
                    'config', 'localization_ekf_master.yaml'))
    
    use_sim_time = LaunchConfiguration('use_sim_time')
    declare_use_sim_time_argument = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation/Gazebo clock')
    
    slam_params_file = LaunchConfiguration('slam_params_file')
    declare_slam_params_file_cmd = DeclareLaunchArgument(
        'slam_params_file',
        default_value=os.path.join(get_package_share_directory("rover_bringup"),
                                   'config', 'slam_sim_params_online_master.yaml'),
        description='Full path to the ROS2 parameters file to use for the slam_toolbox node')

   

    rl_launch_path = os.path.join(get_package_share_directory("rover_bringup"),
                                   'launch', 
                                   'sim_robot_localizer.launch.py')
    
    robot_localizer_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rl_launch_path),
        launch_arguments={'use_sim_time': use_sim_time,
                          'namespace':namespace,
                          'ekf_params_file':ekf_params_file}.items())

    start_async_slam_toolbox_node = Node(
        parameters=[
          slam_params_file,
          {'use_sim_time': use_sim_time}
        ],
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',

        namespace=namespace,
        output='screen',
        
        remappings=[
            
                    ('/odom', ['/',namespace,'/odom']),
                    ('/map', ['/',namespace,'/map']),
                    ('/pose', ['/',namespace,'/pose']),
                    ('/scan',['/',namespace,'/scan']),
                    ('/set_pose',['/',namespace,'/set_pose']),
                    # ('/slam_toolbox/feedback','/master/slam_toolbox/feedback'),
                    # ('/slam_toolbox/update','/master/slam_toolbox/update'),
                    # ('/slam_toolbox/graph_visualization','/master/slam_toolbox/graph_visualization'),
                    # ('/slam_toolbox/scan_visualization','/master/slam_toolbox/scan_visualization'),
                    # ('/odometry/filtered','/master/odometry/filtered'),
                    # ('/map_metadata','/master/map_metadata')
                    ],
        
        
        
    )
   

    ld = LaunchDescription()

    # Add sim time arg
    ld.add_action(declare_use_sim_time_argument)
    
    # Add localization to launch description
    ld.add_action(robot_localizer_launch)
    ld.add_action(declare_namespace)
    ld.add_action(declare_ekf_params_file_cmd)
    # Add slam setup to launch description
    ld.add_action(declare_slam_params_file_cmd)
    ld.add_action(start_async_slam_toolbox_node)
   
    return ld