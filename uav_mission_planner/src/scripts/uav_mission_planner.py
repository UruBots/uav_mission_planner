#!/usr/bin/env python
import time
import rospy
from mavros_controller import MavrosController

controller = MavrosController()
simulation = rospy.get_param('simulation', True)
print("#####################", simulation)
if simulation:
    controller.simulation = simulation

def go_to_destination(dest = "2.0, 0.0, 0.0, 0.0"):
    x, y, z, w = dest.split(",")
    print("setGuidedMode")
    controller.setGuidedMode()
    time.sleep(1)
    print("pub_reset_gps")
    controller.pub_reset_gps()
    time.sleep(1)
    print("/mavros/vision_pose/tf/listen")
    rospy.set_param("/mavros/vision_pose/tf/listen", True)
    time.sleep(5)
    print("setArm")
    controller.setArm()
    time.sleep(1)
    print("setTakeoffMode")
    controller.setTakeoffMode()
    time.sleep(5)
    print("set_target_position")
    controller.set_target_position(x, y, z, w)
    time.sleep(10)
    print("setLandMode")
    controller.setLandMode()
    time.sleep(1)
    print("setDisarm")
    controller.setDisarm()

def read_qr_and_go_to_destination():
    controller.setGuidedMode()
    time.sleep(1)
    controller.pub_reset_gps()
    time.sleep(1)
    rospy.set_param("/mavros/vision_pose/tf/listen", True)
    time.sleep(5)
    controller.setArm()
    time.sleep(1)
    controller.setTakeoffMode()
    time.sleep(15)
    # read qr codes with node.
    time.sleep(1)
    controller.setDisarm()

def menu():
    print("Press")
    print("1: to set mode to GUIDED")
    print("2: to set mode to STABILIZE")
    print("3: to set mode to ARM the drone")
    print("4: to set mode to DISARM the drone")
    print("5: to set mode to TAKEOFF")
    print("6: to set mode to LAND")
    print("7: print GPS coordinates")
    print("8: Go to destination")
    print("9: Read QR-Codes")
    print("10: fakegps")

def myLoop():
    x='1'
    while ((not rospy.is_shutdown())and (x in ['1','2','3','4','5','6','7','8','9', '10'])):
        menu()
        x = input("Enter your input: ")
        if (x=='1'):
            controller.setGuidedMode()
        elif(x=='2'):
            controller.setStabilizeMode()
        elif(x=='3'):
            controller.setArm()
        elif(x=='4'):
            controller.setDisarm()
        elif(x=='5'):
            controller.setTakeoffMode()
        elif(x=='6'):
            controller.setLandMode()
        elif(x=='7'):
            global latitude
            global longitude
            print ("longitude: %.7f" %longitude)
            print ("latitude: %.7f" %latitude)
        elif(x=='8'):
            #dest = raw_input("Enter location to go : example 2.8, 0.0, 2.0, 2.0")
            dest = "1.0,0.0,1.0,0.3"
            go_to_destination(dest)
        elif(x=='9'):
            read_qr_and_go_to_destination()
        elif(x=='10'):
            controller.pub_reset_gps()
        else:
            print("Exit")

def state_callback(data):
    rospy.rospy.loginfo("info Mode: %s" %data.mode)
    if data.mode == "MANUAL":
        #TODO review functionality
        rospy.loginfo("Control connected!!!")
    else:
        myLoop()


if __name__ == '__main__':
    try:
        rospy.init_node('uav_mission_planner', anonymous=True)
        # rospy.Subscriber("/mavros/global_position/raw/fix", NavSatFix, globalPositionCallback)
        # state = rospy.Subscriber('/mavros/state', State, state_callback)
        # TODO check with subscription to state
        myLoop()
        # rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("#### Exception uav ####")

