#!/usr/bin/env python3

import threading
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix
from mavros_msgs.srv import SetMode, CommandBool, CommandTOL
from geographic_msgs.msg import GeoPointStamped
from geometry_msgs.msg import PoseStamped


class UAVMissionPlanner(Node):
    def __init__(self):
        super().__init__('uav_mission_planner')

        # QoS Profile
        self.qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE
        )

        # Publishers
        self.set_point_pub = self.create_publisher(PoseStamped, "/mavros/setpoint_position/local", self.qos)
        self.reset_gps_pub = self.create_publisher(GeoPointStamped, "/mavros/global_position/set_gp_origin", self.qos)

        # Subscribers
        self.create_subscription(PoseStamped, "/mavros/vision_pose/pose", self.local_position_callback, self.qos)
        self.create_subscription(NavSatFix, "/mavros/global_position/raw/fix", self.global_position_callback, self.qos)

        # Service Clients
        self.set_mode_client = self.create_client(SetMode, "/mavros/set_mode")
        self.arm_client = self.create_client(CommandBool, "/mavros/cmd/arming")
        self.takeoff_client = self.create_client(CommandTOL, "/mavros/cmd/takeoff")
        self.land_client = self.create_client(CommandTOL, "/mavros/cmd/land")

        # Variables
        self.latitude = 0.0
        self.longitude = 0.0
        self.local_position = None
        self.pose = PoseStamped()
        self.mission = 1
        self.distanceQRx = 1.25
        self.distanceQRy = 1.38
        self.latest_qr = None

    def local_position_callback(self, data):
        self.local_position = data

    def global_position_callback(self, data):
        self.latitude = data.latitude
        self.longitude = data.longitude

    def set_mode(self, mode, mode_ID):
        if not self.set_mode_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("Set mode service not available")
            return
        request = SetMode.Request(custom_mode=mode_ID)
        future = self.set_mode_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info(f"Set mode to {mode}: {future.result().mode_sent}")
        else:
            self.get_logger().error("Set mode service call failed")

    def pub_reset_gps(self):
        msg = GeoPointStamped()
        self.reset_gps_pub.publish(msg)

    def set_arm(self):
        if not self.arm_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("Arm service not available")
            return
        request = CommandBool.Request(value=True)
        future = self.arm_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info(f"Armed: {future.result().success}")
        else:
            self.get_logger().error("Arm service call failed")

    def set_disarm(self):
        if not self.arm_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("Disarm service not available")
            return
        request = CommandBool.Request(value=False)
        future = self.arm_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info(f"Disarmed: {future.result().success}")
        else:
            self.get_logger().error("Disarm service call failed")

    def set_takeoff_mode(self):
        if not self.takeoff_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("Takeoff service not available")
            return
        request = CommandTOL.Request(altitude=1.0)
        future = self.takeoff_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info(f"Takeoff: {future.result().success}")
        else:
            self.get_logger().error("Takeoff service call failed")

    def set_land_mode(self):
        if not self.land_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("Land service not available")
            return
        request = CommandTOL.Request(altitude=0.0)
        future = self.land_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info(f"Landed: {future.result().success}")
        else:
            self.get_logger().error("Land service call failed")

    def set_guided_mode(self):
        self.set_mode('GUIDED', 'GUIDED')

    def set_stabilize_mode(self):
        self.set_mode('STABILIZE', 'STABILIZE')

    def go_to_destination(self, dest="1.0, 0.0, 1.0, 0.0"):
        x, y, z, w = dest.split(",")
        self.set_guided_mode()
        time.sleep(1)
        self.pub_reset_gps()
        time.sleep(1)
        self.set_arm()
        time.sleep(1)
        self.set_takeoff_mode()
        time.sleep(5)
        self.set_target_position(float(x), float(y), float(z), float(w))
        time.sleep(1)
        self.set_takeoff_mode()
        time.sleep(1)
        self.set_disarm()

    def set_target_position(self, x, y, z=1.0, w=0.0):
        pose_local = PoseStamped()
        pose_local.pose.position.x = x
        pose_local.pose.position.y = y
        pose_local.pose.position.z = z
        pose_local.pose.orientation.w = w
        self.set_point_pub.publish(pose_local)

    def string_to_pose(self, input_string):
        parts = input_string.replace('data: ', '').replace('"', '').split(',')
        if len(parts) != 5:
            raise ValueError("Input string should have 5 comma-separated values")
        if parts[-1] == '0':
            if parts[self.mission - 1] == 'N':
                self.pose.pose.position.x += self.distanceQRx
                self.pose.pose.position.y += 0.0
            elif parts[self.mission - 1] == 'E':
                self.pose.pose.position.x += 0.0
                self.pose.pose.position.y += -self.distanceQRy
            elif parts[self.mission - 1] == 'S':
                self.pose.pose.position.x += -self.distanceQRx
                self.pose.pose.position.y += 0.0
            elif parts[self.mission - 1] == 'W':
                self.pose.pose.position.x += 0.0
                self.pose.pose.position.y += self.distanceQRy
        return self.pose, parts[4]

    def read_qr_and_go_to_destination(self, direction):
        self.mission = 1
        try:
            if self.local_position is not None:
                self.set_guided_mode()
                self.pub_reset_gps()
                time.sleep(5)
                self.set_arm()
                time.sleep(5)
                self.set_takeoff_mode()
                time.sleep(5)
                if direction == 'right':
                    self.set_target_position(0.0, -8.0, 1.0)
                else:
                    self.set_target_position(0.0, 8.0, 1.0)
                time.sleep(1.5)

                while rclpy.ok():
                    qr_detected = self.wait_for_qr_code()
                    if qr_detected:
                        self.latest_qr = qr_detected
                        self.get_logger().info(f"QR Code detected: {qr_detected}")
                        pose, self.target_flag = self.string_to_pose(qr_detected)
                    else:
                        self.get_logger().info("QR Code not detected")
                        break

                    self.set_target_position(self.pose.pose.position.x, self.pose.pose.position.y)
                    if self.target_flag == '4':
                        break
        except Exception as e:
            self.get_logger().error(f"Exception read_qr_and_go_to_destination: {e}")
            self.set_land_mode()

    def wait_for_qr_code(self):
        qr_sub = self.create_subscription(String, '/qrcode/raw', lambda msg: setattr(self, 'qr_msg', msg), self.qos)
        start_time = time.time()
        while time.time() - start_time < 10.0:
            rclpy.spin_once(self, timeout_sec=0.1)
            if hasattr(self, 'qr_msg'):
                qr_sub.destroy()
                return self.qr_msg.data
        qr_sub.destroy()
        return None

    def menu(self):
        self.get_logger().info("Press:")
        self.get_logger().info("1: to set mode to GUIDED")
        self.get_logger().info("2: to set mode to STABILIZE")
        self.get_logger().info("3: to ARM the drone")
        self.get_logger().info("4: to DISARM the drone")
        self.get_logger().info("5: to TAKEOFF")
        self.get_logger().info("6: to LAND")
        self.get_logger().info("7: print GPS coordinates")
        self.get_logger().info("8: Go to destination")
        self.get_logger().info("9: Read QR-Codes (Right)")
        self.get_logger().info("10: Reset GPS")
        self.get_logger().info("11: Read QR-Codes (Left)")

    def my_loop(self):
        while rclpy.ok():
            self.menu()
            x = input("Enter your input: ")
            if x == '1':
                self.set_guided_mode()
            elif x == '2':
                self.set_stabilize_mode()
            elif x == '3':
                self.set_arm()
            elif x == '4':
                self.set_disarm()
            elif x == '5':
                self.set_takeoff_mode()
            elif x == '6':
                self.set_land_mode()
            elif x == '7':
                self.get_logger().info(f"longitude: {self.longitude:.7f}")
                self.get_logger().info(f"latitude: {self.latitude:.7f}")
            elif x == '8':
                self.go_to_destination("1.0,0.0,1.0,0.3")
            elif x == '9':
                self.read_qr_and_go_to_destination("right")
            elif x == '10':
                self.pub_reset_gps()
            elif x == '11':
                self.read_qr_and_go_to_destination("left")


def main(args=None):
    rclpy.init(args=args)
    mission_planner = UAVMissionPlanner()

    # Run the input loop in a separate thread to avoid blocking ROS2 callbacks
    input_thread = threading.Thread(target=mission_planner.my_loop)
    input_thread.start()

    try:
        rclpy.spin(mission_planner)
    except KeyboardInterrupt:
        mission_planner.set_land_mode()
    finally:
        mission_planner.destroy_node()
        rclpy.shutdown()
        input_thread.join()


if __name__ == '__main__':
    main()