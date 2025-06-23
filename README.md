
# ZED RTAB-Map SLAM

![Land Scan](media/land_scan.gif)

## Overview

This repository provides a simple package for integrating RTAB-Map SLAM with the ZED Mini camera using the ZED ROS 2 wrapper. It is compatible with both standard laptops and NVIDIA Jetson devices (tested on Jetson Orin).

## Prerequisites

- [Ubuntu 22.04 (Jammy Jellyfish)](https://releases.ubuntu.com/jammy/)
- [ZED SDK](https://www.stereolabs.com/developers/release/latest/) v4.2 or later
- [CUDA](https://developer.nvidia.com/cuda-downloads)
- ROS 2 [Humble](https://docs.ros.org/en/humble/Installation/Linux-Install-Debians.html)

## Setup Steps

### Install Dependencies

We'll install the `zed-ros2-wrapper` and `zed-ros2-examples` from source, and the RTAB-Map packages from binaries:

```bash
sudo apt update
sudo apt install ros-humble-rtabmap-ros
```

### Build the Package

Clone the wrapper into your ROS 2 workspace and build it:

```bash
# Create a ROS 2 workspace if you don't have one
mkdir -p ~/ros2_ws/src/
cd ~/ros2_ws/src/
git clone https://github.com/stereolabs/zed-ros2-wrapper.git
cd ..
sudo apt update

# Install dependencies
rosdep install --from-paths src --ignore-src -r -y

# Build
colcon build --symlink-install --cmake-args=-DCMAKE_BUILD_TYPE=Release

# Set up environment variables
echo "source $(pwd)/install/local_setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## Running the Code

### ZED Wrapper

To start the ZED node, use:

```bash
ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zedm
```

The `zed_camera.launch.py` script uses [manual composition](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Composition.html) to start the ZED node, loading the appropriate YAML parameters and generating the static TF tree from a [xacro](https://index.ros.org/p/xacro/) file.

> **Note**: You can customize the configuration by editing YAML files like `common_stereo.yaml`, `zed.yaml`, `zedm.yaml`, etc., found in [`zed_wrapper/config`](https://github.com/stereolabs/zed-ros2-wrapper/tree/master/zed_wrapper/config).

#### Using RViz 2

To visualize the ZED data in RViz 2:

```bash
ros2 launch zed_display_rviz2 display_zed_cam.launch.py camera_model:=zedm
```

### ZED's Spatial Mapping

You can perform spatial mapping with just the ZED wrapper and save a `.ply` file of the surroundings.

1. Enable mapping:

```bash
ros2 service call /zed/zed_node/enable_mapping std_srvs/srv/SetBool "data: true"
```

2. Start the custom service to save the fused point cloud:

```bash
ros2 run custom_pkg save_pointcloud_service
```

3. After scanning, save the point cloud:

```bash
ros2 service call /save_pointcloud std_srvs/srv/SetBool "data: true"
```

Make sure to set the desired output path in `save_pointcloud_service.py`.

### ZED vs. RTAB-Map SLAM

| **Feature / Aspect** | **ZED SDK Spatial Mapping** | **RTAB-Map SLAM**             |
| -------------------------- | --------------------------------- | ----------------------------------- |
| **SLAM Capability**  | ❌ VIO only (no loop closure)     | ✅ Full SLAM                        |
| **Loop Closure**     | ❌ Not supported                  | ✅ Supported                        |
| **Relocalization**   | ❌ No                             | ✅ Yes                              |
| **Output**           | ✅ Dense point cloud / mesh       | ✅ Sparse 2D/3D map + point cloud   |
| **Mapping Scale**    | 🔸 Small to medium areas          | ✅ Large environments               |
| **Persistence**      | ✅ Save/load meshes               | ✅ Save/load databases              |
| **Sensor Fusion**    | ✅ Stereo + IMU (ZED)             | ✅ ZED + other sensors (GPS, LiDAR) |
| **Use Case**         | 🔸 Quick 3D scans / local maps    | ✅ Long-term SLAM, navigation       |

## RTAB-Map SLAM with ZED

1. Launch the ZED node as before:

```bash
ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zedm
```

2. Launch the custom launch file for RTAB-Map:

```bash
ros2 launch custom_pkg zed_rtabmap.launch.py
```

This file will:

- Remap ZED topics
- Launch the RTAB-Map node
- Launch a custom measurement node that monitors GPU, CPU, and RAM usage during SLAM and logs it to `/measurements/*.csv`

### Saving the RTAB-Map Database

Once finished, save the `.db` file (contains loop closures, map, and point clouds):

```bash
cp ~/.ros/rtabmap.db ~/rtabmap_maps/rtabmap_2025_06_08-EXP01.db
```

You can inspect and export maps from the database using:

```bash
rtabmap-databaseViewer
```
