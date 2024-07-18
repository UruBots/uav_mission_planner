

import time
import rospy
from std_msgs.msg import *
from sensor_msgs.msg import *
from mavros_msgs.srv import *
from mavros_msgs.msg import *
from geographic_msgs.msg import *
from geometry_msgs.msg import *
from status import Status

#global variable
latitude = 0.0
longitude = 0.0

class MavrosController(object):
    def __init__(self):
	    self.status = Status.NotInited
     
    def set_status(self, status):
        self.status = status

    def call_set_mode(mode, mode_ID):
        try:
            service = rospy.ServiceProxy("/mavros/set_mode", SetMode)
            rospy.wait_for_service("/mavros/set_mode")
            print(service(mode_ID, mode))
        except rospy.ServiceException as e:
            print('Service call failed: %s' % e)

    # TODO change to call_set_mode
    #http://wiki.ros.org/mavros/CustomModes for custom modes
    def setGuidedMode():
        rospy.wait_for_service('/mavros/set_mode')
        try:
            flightModeService = rospy.ServiceProxy('/mavros/set_mode', mavros_msgs.srv.SetMode)
            isModeChanged = flightModeService(custom_mode='GUIDED') #return true or false
        except rospy.ServiceException as e:
            print("service set_mode call failed: %s. GUIDED Mode could not be set. Check that GPS is enabled" % e)

    # TODO change to call_set_mode
    def setStabilizeMode():
        rospy.wait_for_service('/mavros/set_mode')
        try:
            flightModeService = rospy.ServiceProxy('/mavros/set_mode', mavros_msgs.srv.SetMode)
            isModeChanged = flightModeService(custom_mode='STABILIZE') #return true or false
        except rospy.ServiceException as e:
            print("service set_mode call failed: %s. GUIDED Mode could not be set. Check that GPS is enabled" % e)

    def setLandMode():
        rospy.wait_for_service('/mavros/cmd/land')
        try:
            landService = rospy.ServiceProxy('/mavros/cmd/land', mavros_msgs.srv.CommandTOL)
            isLanding = landService(altitude = 0, latitude = 0, longitude = 0, min_pitch = 0, yaw = 0)
        except rospy.ServiceException as e:
            print("service land call failed: %s. The vehicle cannot land " % e)
            
    def setArm(self):
        self.pub_reset_gps()
        time.sleep(1)
        rospy.wait_for_service('/mavros/cmd/arming')
        try:
            # TODO this is to verify why the drone is arming but not launching
            rospy.set_param("/mavros/vision_pose/tf/listen", True)
            self.pub_reset_gps()

            armService = rospy.ServiceProxy('/mavros/cmd/arming', mavros_msgs.srv.CommandBool)
            armService(True)
        except rospy.ServiceException as e:
            print("Service arm call failed: %s"%e)
            
    def setDisarm():
        rospy.wait_for_service('/mavros/cmd/arming')
        try:
            armService = rospy.ServiceProxy('/mavros/cmd/arming', mavros_msgs.srv.CommandBool)
            armService(False)
        except rospy.ServiceException as e:
            print("Service arm call failed: %s"%e)


    def setTakeoffMode():
        rospy.wait_for_service('/mavros/cmd/takeoff')
        try:
            takeoffService = rospy.ServiceProxy('/mavros/cmd/takeoff', mavros_msgs.srv.CommandTOL) 
            takeoffService(altitude = 0.5, latitude = 0, longitude = 0, min_pitch = 0, yaw = 0)
        except rospy.ServiceException as e:
            print("Service takeoff call failed: %s" % e)

    def globalPositionCallback(globalPositionCallback):
        global latitude
        global longitude
        latitude = globalPositionCallback.latitude
        longitude = globalPositionCallback.longitude
        #print ("longitude: %.7f" %longitude)
        #print ("latitude: %.7f" %latitude)

    def set_target_position(x,y,z,w):
        pose = PoseStamped()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        pose.pose.orientation.w = w
        try:
            set_point_pub = rospy.Publisher("/mavros/setpoint_position/local", PoseStamped, queue_size=10)
            set_point_pub.publish(pose)
        except rospy.ServiceException as e:
            print("Service set_target_position call failed: %s" % e)

    def pub_reset_gps():
        msg = GeoPointStamped()
        try:
            reset_gps = rospy.Publisher("/mavros/global_position/set_gp_origin", GeoPointStamped, queue_size=10)
            reset_gps.publish(msg)
        except rospy.ServiceException as e:
            print("Service reset_gps call failed: %s" % e)
            
    # TODO status is not being used
    # utils functions
    def start_drone(self):
        self.setGuidedMode()
        time.sleep(1)
        self.pub_reset_gps()
        time.sleep(1)
        rospy.set_param("/mavros/vision_pose/tf/listen", True)
        time.sleep(5)
        self.setArm()
        time.sleep(1)
        self.setTakeoffMode()
        
    def end_drone(self):
        self.setLandMode()
        self.setDisarm()
        self.setStabilizeMode()
        self.status = Status.Landed