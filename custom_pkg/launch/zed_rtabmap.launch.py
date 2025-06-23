from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os

def generate_launch_description():
    pkg_dir = os.path.dirname(__file__)  # use current package directory
    camera_model = 'zed'
    rtabmap_config_path = os.path.join(pkg_dir, 'config/rtabmap_params.yaml')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_dir, 'rtabmap_original.launch.py')
            ),
            launch_arguments={
                #'use_sim_time': 'false',
                'frame_id': 'zed_camera_link',
                #'subscribe_rgbd': 'false',
                #'subscribe_depth': 'true',
                'visual_odometry': 'false',
                'approx_sync': 'true',
                'rgb_topic': f'/{camera_model}/zed_node/rgb/image_rect_color',
                'depth_topic': f'/{camera_model}/zed_node/depth/depth_registered',
                'camera_info_topic': f'/{camera_model}/zed_node/rgb/camera_info',
                'odom_topic': f'/{camera_model}/zed_node/odom',
                'config_path': rtabmap_config_path,
            }.items(),
            
        ),
        
        # # Launch custom service node
        # Node(
        #     package='custom_pkg',
        #     executable='save_pointcloud_service',
        #     name='save_pointcloud_service_node',
        #     output='screen'
        # ),

        # Launch measure node
        Node(
            package='custom_pkg',
            executable='measure',  # This must match the name declared in setup.py entry_points
            name='measure_node',
            output='screen'
        )
    ])
