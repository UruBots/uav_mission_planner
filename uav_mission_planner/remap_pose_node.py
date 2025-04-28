#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
from mavros_msgs.msg import State


class RemapPoseNode(Node):
    def __init__(self):
        # Initialize the ROS2 node
        super().__init__("remap_pose_node")

        # Global variables to store the current state and odometry data
        self.px4_current_state = State()
        self.zed_current_odom = Odometry()
        self.zed_current_odom_cov = PoseWithCovarianceStamped()

        # Subscribers
        self.subscription_px4_state = self.create_subscription(
            State,
            "/mavros/state",
            self.px4_state_cb,
            10  # QoS profile depth
        )
        self.subscription_zed_odom = self.create_subscription(
            PoseStamped,
            "/zedm/zed_node/pose",
            self.zed_odom_cb,
            10  # QoS profile depth
        )
        self.subscription_zed_odom_cov = self.create_subscription(
            PoseWithCovarianceStamped,
            "/zedm/zed_node/pose_with_covariance",
            self.zed_odom_cov_cb,
            10  # QoS profile depth
        )

        # Publishers
        self.vision_pose_pub_cov = self.create_publisher(
            PoseWithCovarianceStamped,
            "/mavros/vision_pose/pose_cov",
            10  # QoS profile depth
        )
        self.vision_pose_pub = self.create_publisher(
            PoseStamped,
            "/mavros/vision_pose/pose",
            10  # QoS profile depth
        )

        # Timer for main loop (45 Hz)
        self.timer = self.create_timer(1.0 / 45, self.timer_callback)

        # Wait until PX4 is connected
        self.wait_for_px4_connection()

    def px4_state_cb(self, msg):
        """Callback function for PX4 state updates."""
        self.px4_current_state = msg

    def zed_odom_cb(self, msg):
        """Callback function for ZED odometry updates."""
        self.zed_current_odom.pose = msg.pose

    def zed_odom_cov_cb(self, msg):
        """Callback function for ZED odometry with covariance updates."""
        self.zed_current_odom_cov = msg

    def wait_for_px4_connection(self):
        """Wait until PX4 is connected."""
        while rclpy.ok() and not self.px4_current_state.connected:
            self.get_logger().info("Waiting for PX4 connection...")
            rclpy.spin_once(self, timeout_sec=0.1)

    def timer_callback(self):
        """Main loop callback."""
        self.get_logger().info("Remapping vision pose information message!")

        # Debugging print statements
        self.get_logger().info(f"#### zed_current_odom: {self.zed_current_odom.pose}")
        self.get_logger().info(f"#### zed_current_odom_cov: {self.zed_current_odom_cov.pose}")

        # Create PoseStamped message
        cur_pose = PoseStamped()
        cur_pose.header.frame_id = "odom"
        cur_pose.header.stamp = self.get_clock().now().to_msg()
        cur_pose.pose = self.zed_current_odom.pose

        # Create PoseWithCovarianceStamped message
        cur_pose_cov = PoseWithCovarianceStamped()
        cur_pose_cov.header.frame_id = "odom"
        cur_pose_cov.header.stamp = self.get_clock().now().to_msg()
        cur_pose_cov.pose = self.zed_current_odom_cov.pose

        # Publish messages
        self.vision_pose_pub.publish(cur_pose)
        self.vision_pose_pub_cov.publish(cur_pose_cov)
        self.get_logger().info("Published remapped poses.")


def main(args=None):
    # Initialize the ROS2 Python client
    rclpy.init(args=args)

    # Create the remap pose node
    remap_pose_node = RemapPoseNode()

    try:
        # Spin the node to process callbacks
        rclpy.spin(remap_pose_node)
    except KeyboardInterrupt:
        # Handle shutdown gracefully
        remap_pose_node.get_logger().info("Shutting down remap pose node.")
    finally:
        # Destroy the node and shut down ROS2
        remap_pose_node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()