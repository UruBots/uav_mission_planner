# import time
import rospy
from std_msgs.msg import *
from sensor_msgs.msg import *
from mavros_msgs.srv import *
from mavros_msgs.msg import *
from geographic_msgs.msg import *
from geometry_msgs.msg import *
from status import Status
import os

#global variable
latitude = 0.0
longitude = 0.0

class MavrosController(object):
    def __init__(self):
        self.status = Status.NotInited
        self.simulation = rospy.get_param('simulation', False)
        print("#### MavrosController simulation ####", self.simulation)
        if self.simulation:
            self.set_point_pub = rospy.Publisher("/uav1/mavros/local_position/pose", PoseStamped, queue_size=10)
        else:
            self.set_point_pub = rospy.Publisher("/mavros/setpoint_position/local", PoseStamped, queue_size=10)

    def set_status(self, status):
        self.status = status

    def call_set_mode(mode, mode_ID):
        try:                
            service = rospy.ServiceProxy("/mavros/set_mode", SetMode)
            rospy.wait_for_service("/mavros/set_mode")
            print(service(mode_ID, mode))
        except rospy.ServiceException as e:
            print('Service call failed: %s' % e)

    def set_pose(self, x, y, z):
        pose = PoseStamped()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        pose.pose.orientation.x = 0
        pose.pose.orientation.y = 0
        pose.pose.orientation.z = 0
        pose.pose.orientation.w = 1
        return pose

    def go_to(self, x,y,z):
        try:
            pose = self.set_pose(x, y, z)
            print("#### NEW POSE ####", pose)
            # if self.simulation:
            #     service = rospy.ServiceProxy("/mavros/set_mode", )
            self.set_point_pub.publish(pose)
        except rospy.ServiceException as e:
            print("Service set_target_position call failed: %s" % e)

    # TODO change to call_set_mode
    #http://wiki.ros.org/mavros/CustomModes for custom modes
    def setGuidedMode(self):
        try:
            if self.simulation:
                print("setGuidedMode simulated")
                flightModeService = rospy.ServiceProxy('/uav1/mavros/set_mode', SetMode)
                isModeChanged = flightModeService(custom_mode='AUTO.LAND') #return true or false
            else:
                rospy.wait_for_service('/mavros/set_mode')
                flightModeService = rospy.ServiceProxy('/mavros/set_mode', SetMode)
                isModeChanged = flightModeService(custom_mode='GUIDED') #return true or false
        except rospy.ServiceException as e:
            print("service set_mode call failed: %s. GUIDED Mode could not be set. Check that GPS is enabled" % e)

    # TODO change to call_set_mode
    def setStabilizeMode(self):
        try:
            if self.simulation:
                print("setStabilizeMode simulated")
                flightModeService = rospy.ServiceProxy('/uav1/mavros/set_mode', SetMode)
            else:
                rospy.wait_for_service('/mavros/set_mode')
                flightModeService = rospy.ServiceProxy('/mavros/set_mode', SetMode)
            isModeChanged = flightModeService(custom_mode='STABILIZE') #return true or false
        except rospy.ServiceException as e:
            print("service set_mode call failed: %s. GUIDED Mode could not be set. Check that GPS is enabled" % e)

    def setLandMode(self):
        try:
            if self.simulation:
                print("setLandMode simulated")
                landService = rospy.ServiceProxy('/uav1/mavros/cmd/land', CommandTOL)
            else:
                rospy.wait_for_service('/mavros/cmd/land')
                landService = rospy.ServiceProxy('/mavros/cmd/land', CommandTOL)
            isLanding = landService(altitude = 0, latitude = 0, longitude = 0, min_pitch = 0, yaw = 0)
        except rospy.ServiceException as e:
            print("service land call failed: %s. The vehicle cannot land " % e)
            
    def setArm(self):
        try:
            if self.simulation:
                print("setArm simulated")
                # armService = rospy.ServiceProxy('/uav1/mavros/cmd/arming', CommandBool)
                cmd = 'rosservice call /uav1/hw_api/arming 1 && sleep 1 && rosservice call /uav1/hw_api/offboard'
                os.system(cmd)
            else:
                # TODO this is to verify why the drone is arming but not launching
                rospy.set_param("/mavros/vision_pose/tf/listen", True)
                self.pub_reset_gps()

                rospy.wait_for_service('/mavros/cmd/arming')    
                armService = rospy.ServiceProxy('/mavros/cmd/arming',CommandBool)
                armService(True)
        except rospy.ServiceException as e:
            print("Service arm call failed: %s"%e)
            
    def setDisarm(self):
        try:
            if self.simulation:
                print("setDisarm simulated")
                armService = rospy.ServiceProxy('/uav1/mavros/cmd/arming', CommandBool)
            else:
                rospy.wait_for_service('/mavros/cmd/arming')
                armService = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)
            armService(False)
        except rospy.ServiceException as e:
            print("Service arm call failed: %s"%e)


    def setTakeoffMode(self):
        try:
            if self.simulation:
                print("setTakeoffMode simulated")
                takeoffService = rospy.ServiceProxy('/uav1/mavros/cmd/takeoff', CommandTOL)
            else:
                rospy.wait_for_service('/mavros/cmd/takeoff')
                takeoffService = rospy.ServiceProxy('/mavros/cmd/takeoff', CommandTOL) 
            takeoffService(altitude = 1, latitude = 0, longitude = 0, min_pitch = 0, yaw = 0)
        except rospy.ServiceException as e:
            print("Service takeoff call failed: %s" % e)

    def globalPositionCallback(globalPositionCallback):
        global latitude
        global longitude
        latitude = globalPositionCallback.latitude
        longitude = globalPositionCallback.longitude
        #print ("longitude: %.7f" %longitude)
        #print ("latitude: %.7f" %latitude)

    def set_target_position(self, x, y, z, w):
        pose = PoseStamped()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        pose.pose.orientation.w = w
        try:
            if self.simulation:
                # /uav1/mavros/setpoint_raw/local
                # /uav1/mavros/global_position/global
                # /uav1/mavros/setpoint_raw/target_local
                set_point_pub = rospy.Publisher("/uav1/mavros/setpoint_raw/target_local", PoseStamped, queue_size=10)
            else:
                set_point_pub = rospy.Publisher("/mavros/setpoint_position/local", PoseStamped, queue_size=10)
            set_point_pub.publish(pose)
        except rospy.ServiceException as e:
            print("Service set_target_position call failed: %s" % e)

    def pub_reset_gps(self):
        msg = GeoPointStamped()
        try:
            if self.simulation:
                print("pub_reset_gps simulated")
                reset_gps = rospy.Publisher("/uav1/mavros/global_position/set_gp_origin", GeoPointStamped, queue_size=10)
            else:
                reset_gps = rospy.Publisher("/mavros/global_position/set_gp_origin", GeoPointStamped, queue_size=10)
            reset_gps.publish(msg)
        except rospy.ServiceException as e:
            print("Service reset_gps call failed: %s" % e)
            
    # TODO status is not being used
    # utils functions
    def fly_drone(self):
        print("setGuidedMode")
        self.setGuidedMode()
        # time.sleep(1)
        rospy.Rate(1).sleep()
        print("pub_reset_gps")
        self.pub_reset_gps()
        # time.sleep(1)
        rospy.Rate(1).sleep()
        rospy.set_param("/mavros/vision_pose/tf/listen", True)
        # time.sleep(5)
        rospy.Rate(5).sleep()
        print("setArm 1")
        self.setArm()
        # time.sleep(1)
        rospy.Rate(1).sleep()
        print("setArm 2")
        self.setArm()
        # time.sleep(1)
        rospy.Rate(1).sleep()
        print("setTakeoffMode")
        self.setTakeoffMode()
        rospy.Rate(5).sleep()
        self.go_to(0.5, 0, 0.5)
        rospy.Rate(5).sleep()

        
    def land_drone(self):
        print("setLandMode")
        self.setLandMode()
        print("setDisarm")
        self.setDisarm()
        print("setStabilizeMode")
        self.setStabilizeMode()
        self.status = Status.Landed