import open3d as o3d

point_cloud = o3d.io.read_point_cloud("/home/ainhoaarnaiz/ros2_ws/src/custom_pkg/pointclouds/fused_cloud_20250607_143835.ply")
o3d.visualization.draw_geometries([point_cloud])