from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = os.path.dirname(__file__)
    zed_pkg_dir = "/home/ainhoaarnaiz/ros2_ws/src/zed-ros2-examples/zed_display_rviz2/launch"

    return LaunchDescription([
        # Launch ZED node
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(zed_pkg_dir, 'display_zed_cam.launch.py')
            ),
            launch_arguments={
                'camera_model': 'zedm',
            }.items(),
        ),
        # Launch RTAB-Map in vo+graph mode
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_dir, 'rtabmap_original.launch.py')
            ),
            launch_arguments={
                'frame_id': 'zed/zed_node/odom',
                'odom_frame_id': 'zed/zed_node/odom',
                'wait_for_transform_duration': '1.0',
                'queue_size': '60',
                'approx_sync': 'true',
                'approx_sync_max_interval': '0.05',
                'create_map': 'true',  # <== KEY LINE
                'rgb_topic': '/zed/zed_node/rgb/image_rect_color',
                'depth_topic': '/zed/zed_node/depth/depth_registered',
                'camera_info_topic': '/zed/zed_node/rgb/camera_info',
                'odom_topic': '/zed/zed_node/odom',
                'rtabmap_viz': 'false',
                'cfg': '/home/ainhoaarnaiz/ros2_ws/src/custom_pkg/config/rtabmap_params_combined.yaml',
            }.items(),
        ),

        # Launch custom service node
        Node(
            package='custom_pkg',
            executable='save_pointcloud_service',  # Replace with actual service node filename (without .py)
            name='save_pointcloud_service_node',
            output='screen'
        ),

        # Launch measure node
        Node(
            package='custom_pkg',
            executable='measure',  # This must match the name declared in setup.py entry_points
            name='measure_node',
            output='screen'
        )
    ])
