#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2


class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')

        # Create a CvBridge to convert OpenCV images to ROS image messages
        self.bridge = CvBridge()

        # Initialize the webcam capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.get_logger().error("Failed to open webcam")
            raise RuntimeError("Webcam not available")

        # Publishers for different image formats
        qos_profile = 10  # QoS profile depth
        self.pub = self.create_publisher(Image, '/camera_1', qos_profile)
        self.rgb8pub = self.create_publisher(Image, '/camera_1/rgb', qos_profile)
        self.bgr8pub = self.create_publisher(Image, '/camera_1/bgr', qos_profile)
        self.mono8pub = self.create_publisher(Image, '/camera_1/mono', qos_profile)

    def run(self):
        while rclpy.ok():
            try:
                # Capture frame from the webcam
                ret, frame = self.cap.read()
                if not ret:
                    self.get_logger().error("Failed to capture frame from webcam")
                    break

                # Publish the raw BGR8 image
                self.pub.publish(self.bridge.cv2_to_imgmsg(frame, "bgr8"))

                # Publish the RGB8 image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.rgb8pub.publish(self.bridge.cv2_to_imgmsg(frame_rgb, "rgb8"))

                # Publish the BGR8 image (same as raw but explicitly published)
                self.bgr8pub.publish(self.bridge.cv2_to_imgmsg(frame, "bgr8"))

                # Publish the MONO8 image
                frame_mono = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.mono8pub.publish(self.bridge.cv2_to_imgmsg(frame_mono, "mono8"))

            except CvBridgeError as e:
                self.get_logger().error(f"CvBridge Error: {e}")
                break

        # Release the webcam when done
        self.cap.release()

def main(args=None):
    # Initialize the ROS2 Python client
    rclpy.init(args=args)

    # Create the image publisher node
    image_publisher = ImagePublisher()

    try:
        # Run the image publishing loop
        image_publisher.get_logger().info("Publishing images from webcam...")
        image_publisher.run()
    except KeyboardInterrupt:
        image_publisher.get_logger().info("Shutting down image publisher node.")
    finally:
        # Destroy the node and shut down ROS2
        image_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()