#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped


class QRtoMove(Node):
    def __init__(self):
        # Initialize the ROS2 node
        super().__init__('qr_to_move')

        # Subscribe to the raw QR code topic
        self.subscription = self.create_subscription(
            String,
            '/qrcode/raw',  # Adjust the topic name if needed
            self.callback,
            10  # QoS profile depth
        )
        self.subscription  # Prevent unused variable warning

        # Publisher for setting position in MAVROS
        self.set_position = self.create_publisher(
            PoseStamped,
            "/mavros/setpoint_position/local",
            10  # QoS profile depth
        )

    def callback(self, data):
        self.get_logger().info(f"###### data: {data.data}")
        pose = self.string_to_pose(data.data)
        self.get_logger().info(f"Publishing pose: {pose}")
        self.set_position.publish(pose)

    def string_to_pose(self, input_string):
        """
        Converts a string representation of a QR code into a PoseStamped message.
        Expected format: "N,0.0,0.0,0.0,1.5" or similar with direction and coordinates.
        """
        # Parse the input string
        parts = input_string.replace('"', '').split(',')

        if len(parts) != 5:
            self.get_logger().error("Input string should have 5 comma-separated values")
            return PoseStamped()

        pose = PoseStamped()
        pose.pose.position.x = 0.0
        pose.pose.position.y = 0.0
        pose.pose.position.z = 0.0

        # Assign orientation based on the direction
        if parts[0] == 'N':
            pose.pose.position.x = 1.0
            pose.pose.position.y = 0.0
            pose.pose.orientation.w = 1.0
        elif parts[0] == 'E':
            pose.pose.position.x = 0.0
            pose.pose.position.y = 1.0
            pose.pose.orientation.w = 0.0
            pose.pose.orientation.z = 1.0
        elif parts[0] == 'S':
            pose.pose.position.x = -1.0
            pose.pose.position.y = 0.0
            pose.pose.orientation.w = -1.0
        elif parts[0] == 'W':
            pose.pose.position.x = 0.0
            pose.pose.position.y = -1.0
            pose.pose.orientation.w = 0.0
            pose.pose.orientation.z = -1.0

        # Assign the target position
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'map'  # Adjust the frame_id as needed
        pose.pose.position.z = float(parts[4])

        return pose


def main(args=None):
    # Initialize the ROS2 Python client
    rclpy.init(args=args)

    # Create the QR-to-Move node
    qr_to_move = QRtoMove()

    try:
        # Spin the node to process callbacks
        rclpy.spin(qr_to_move)
    except KeyboardInterrupt:
        # Handle shutdown gracefully
        qr_to_move.get_logger().info("Shutting down QR-to-Move node.")
    finally:
        # Destroy the node and shut down ROS2
        qr_to_move.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()