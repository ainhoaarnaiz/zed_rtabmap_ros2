#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from std_srvs.srv import SetBool
import sensor_msgs_py.point_cloud2 as pc2
import numpy as np
import os
from datetime import datetime

class PointCloudSaver(Node):
    def __init__(self):  # Fixed: Changed **init** to __init__
        super().__init__('pointcloud_saver')
        self.declare_parameter("output_dir", "/home/path/to/pointclouds") # change directory
        self.pointcloud_sub = self.create_subscription(
            PointCloud2,
            '/zed/zed_node/mapping/fused_cloud',
            self.pointcloud_callback,
            10
        )
        self.srv = self.create_service(SetBool, '/save_pointcloud', self.save_pointcloud_callback)
        self.latest_pointcloud = None
        self.get_logger().info('PointCloud Saver node initialized')

    def pointcloud_callback(self, msg):
        self.latest_pointcloud = msg
        # Optional: Add logging for debug
        # self.get_logger().debug(f"Received point cloud with {msg.width * msg.height} points")
        # 
        #self.get_logger().info(f"Point fields: {[f.name for f in msg.fields]}")


    def save_pointcloud_callback(self, request, response):
        if request.data and self.latest_pointcloud:
            self.get_logger().info('Saving point cloud...')
            try:
                # Convert ROS PointCloud2 to NumPy array
                cloud_points = list(pc2.read_points(self.latest_pointcloud, skip_nans=True))
                if not cloud_points:
                    raise ValueError("Empty point cloud")
                
                # Convert to NumPy array
                points_array = np.array(cloud_points)
                
                # Generate filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = self.get_parameter("output_dir").get_parameter_value().string_value
                os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
                filename = f"{output_dir}/fused_cloud_{timestamp}.ply"
                
                # Save as PLY
                self._save_ply(filename, points_array)
                
                self.get_logger().info(f"Saved point cloud to {filename}")
                response.success = True
                response.message = "Saved point cloud successfully"
            except Exception as e:
                self.get_logger().error(f"Failed to save: {e}")
                response.success = False
                response.message = f"Error: {e}"
        else:
            response.success = False
            response.message = "No point cloud to save or flag was false"
        return response

    def _save_ply(self, filename, points):
        """
        Save point cloud as PLY file using NumPy, unpacking RGB from float32
        :param filename: Output filename
        :param points: NumPy array of points
        """
        with open(filename, 'w') as f:
            # Write PLY header
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {len(points)}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write("property uchar red\n")
            f.write("property uchar green\n")
            f.write("property uchar blue\n")
            f.write("end_header\n")

            for point in points:
                x, y, z, rgb = point
                # Convert float RGB to uint32
                rgb_uint32 = np.frombuffer(np.float32(rgb).tobytes(), dtype=np.uint32)[0]
                r = (rgb_uint32 >> 16) & 0xFF
                g = (rgb_uint32 >> 8) & 0xFF
                b = rgb_uint32 & 0xFF
                f.write(f"{x} {y} {z} {r} {g} {b}\n")


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudSaver()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':  # Fixed: Changed **name** to __name__
    main()