import time
import csv
import subprocess
import re
from datetime import datetime
from ament_index_python.packages import get_package_share_directory
import os

import rclpy
from rclpy.node import Node


class TegrastatsLogger(Node):
    def __init__(self):
        super().__init__('tegrastats_logger')

        # Create the data folder path
        data_dir = '/home/ainhoaarnaiz/ros2_ws/src/custom_pkg/measurements'

        # Create timestamped CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = os.path.join(data_dir, f"tegrastats_log_{timestamp}.csv")

        self.headers = ["Time", "RAM Used (MB)", "RAM Total (MB)", "CPU Avg (%)", "GPU (%)"]

        # Compile regexes
        self.ram_regex = re.compile(r"RAM (\d+)/(\d+)MB")
        self.cpu_regex = re.compile(r"CPU \[([^\]]+)\]")
        self.gpu_regex = re.compile(r"GR3D_FREQ (\d+)%")

        # Open file and write header
        self.file = open(self.filename, "w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow(self.headers)

        self.get_logger().info(f"Logging tegrastats to {self.filename} every second.")
        self.timer = self.create_timer(1.0, self.log_tegrastats)

        # ? Add shutdown handler
        rclpy.get_default_context().on_shutdown(self._on_shutdown)

    def log_tegrastats(self):
        start_time = time.time()

        # Start tegrastats subprocess and capture one line
        process = subprocess.Popen(["/usr/bin/tegrastats"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        line = process.stdout.readline().decode("utf-8").strip()
        process.terminate()

        # Parse values
        ram_match = self.ram_regex.search(line)
        ram_used, ram_total = (ram_match.groups() if ram_match else ("", ""))

        cpu_match = self.cpu_regex.search(line)
        if cpu_match:
            cpu_values = [int(core.split('%')[0]) for core in cpu_match.group(1).split(',')]
            cpu_avg = round(sum(cpu_values) / len(cpu_values), 1)
        else:
            cpu_avg = ""

        gpu_match = self.gpu_regex.search(line)
        gpu = gpu_match.group(1) if gpu_match else ""

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, ram_used, ram_total, cpu_avg, gpu]
        self.writer.writerow(row)
        self.file.flush()

        #self.get_logger().info(f"[{now}] RAM: {ram_used}/{ram_total} MB | CPU: {cpu_avg}% | GPU: {gpu}%")
    
    def _on_shutdown(self):
        if self.file:
            self.get_logger().info("Shutting down: closing CSV file.")
            self.file.close()


def main(args=None):
    rclpy.init(args=args)
    node = TegrastatsLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Logging interrupted by user. File saved successfully.")
    finally:
        node.file.close()
        node.destroy_node()
        rclpy.shutdown()
