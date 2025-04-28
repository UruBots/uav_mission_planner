#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist

class LineFollower(Node):
    def __init__(self):
        # Initialize the ROS2 node
        super().__init__('line_follower')
        
        # Create a CvBridge to convert ROS image messages to OpenCV images
        self.bridge = CvBridge()
        
        # Subscribe to the camera image topic
        self.image_sub = self.create_subscription(
            Image,
            "/camera/image_raw",  # Adjust the topic name if needed
            self.image_callback,
            10  # QoS profile depth
        )
        
        # Publisher for velocity commands
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/mavros/setpoint_velocity/cmd_vel',
            10  # QoS profile depth
        )

    def image_callback(self, data):
        try:
            # Convert ROS image message to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except Exception as e:
            self.get_logger().error(f"CvBridge Error: {e}")
            return
        
        # Process the image and follow the line
        processed_image = self.process_image(cv_image)
        self.follow_line(processed_image)
        
        # Display the result
        cv2.imshow("Line Following", processed_image)
        cv2.waitKey(3)

    def process_image(self, cv_image):
        """
        Process the image to detect lines.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Threshold the image to isolate white lines
        _, thresholded = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find edges for better line detection
        edges = cv2.Canny(thresholded, 50, 150)
        
        # Optionally, apply Hough Line Transform to find lines
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, None, 50, 10)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        return cv_image

    def follow_line(self, processed_image):
        """
        Follow the detected lines by publishing velocity commands.
        """
        # Detect lines using Hough Line Transform
        lines = cv2.HoughLinesP(processed_image, 1, np.pi / 180, 50, None, 50, 10)
        
        # Create a Twist message for velocity commands
        cmd_vel = Twist()
        
        if lines is not None:
            # Example forward speed and angular speed
            cmd_vel.linear.x = 0.5
            cmd_vel.angular.z = 0.1
        else:
            # Stop the robot if no lines are detected
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.0
        
        # Publish the velocity command
        self.cmd_vel_pub.publish(cmd_vel)


def main(args=None):
    # Initialize the ROS2 Python client
    rclpy.init(args=args)
    
    # Create the line follower node
    line_follower = LineFollower()
    
    try:
        # Spin the node to process callbacks
        rclpy.spin(line_follower)
    except KeyboardInterrupt:
        # Handle shutdown gracefully
        line_follower.get_logger().info("Shutting down line follower node.")
    finally:
        # Destroy the node and shut down ROS2
        line_follower.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()