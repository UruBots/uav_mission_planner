#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError
import cv2
from pyzbar.pyzbar import decode

class CameraReader(Node):
    def __init__(self):
        # Initialize the ROS2 node
        super().__init__('camera_read')
        
        # Create a CvBridge to convert ROS image messages to OpenCV images
        self.bridge = CvBridge()
        
        # Subscribe to the camera image topic
        self.subscription = self.create_subscription(
            Image,
            '/camera_1',  # Adjust the topic name if needed
            self.callback,
            10  # QoS profile depth
        )
        self.subscription  # Prevent unused variable warning
        
        # Publisher for processed images with detected QR codes
        self.image_pub = self.create_publisher(
            Image,
            '/camera_1/qrcode',
            10  # QoS profile depth
        )
        
        # Publisher for raw QR code data
        self.qr_to_move = self.create_publisher(
            String,
            '/qrcode/raw',
            10  # QoS profile depth
        )

    def callback(self, data):
        try:
            # Convert ROS image message to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(data, desired_encoding='bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge Error: {e}")
            return

        # Resize the image (adjust dimensions as needed)
        resized_image = cv2.resize(cv_image, (480, 640))

        # Decode QR codes in the image
        qr_result = decode(resized_image)

        if qr_result:
            # Extract QR code data
            qr_data = qr_result[0].data.decode('utf-8')
            self.get_logger().info(f"QR Code detected: {qr_data}")
            
            # Draw a rectangle around the QR code
            (x, y, w, h) = qr_result[0].rect
            cv2.rectangle(resized_image, (x, y), (x + w, y + h), (0, 0, 255), 4)
            
            # Add text label for the QR code
            text = f"{qr_data}"
            cv2.putText(resized_image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Publish the raw QR code data
            qr_msg = String()
            qr_msg.data = qr_data
            self.qr_to_move.publish(qr_msg)
        
        # Convert the processed OpenCV image back to a ROS image message
        try:
            ros_image = self.bridge.cv2_to_imgmsg(resized_image, encoding='bgr8')
            self.image_pub.publish(ros_image)
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge Error: {e}")

def main(args=None):
    # Initialize the ROS2 Python client
    rclpy.init(args=args)
    
    # Create the camera reader node
    camera_reader = CameraReader()
    
    try:
        # Spin the node to process callbacks
        rclpy.spin(camera_reader)
    except KeyboardInterrupt:
        # Handle shutdown gracefully
        camera_reader.get_logger().info("Shutting down camera reader node.")
    finally:
        # Destroy the node and shut down ROS2
        camera_reader.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()