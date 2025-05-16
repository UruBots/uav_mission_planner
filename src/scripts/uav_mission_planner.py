#!/usr/bin/env python3
import time
import rospy
import math
from std_msgs.msg import String
from sensor_msgs.msg import *
from mavros_msgs.srv import *
from mavros_msgs.msg import *
from geographic_msgs.msg import *
from geometry_msgs.msg import *
#from cv_bridge import CvBridge, CvBridgeError

#global variable
latitude = 0.0
longitude = 0.0
qr_code = None
global local_position
local_position = None
global pose_x
global pose_y
global distanceQRy
global distanceQRx
distanceQRx = 1.25
distanceQRy = 1.38
global mission
global pose
pose = PoseStamped()
global base_pose
base_pose = PoseStamped()
global target_flag
target_flag = 0
global latest_qr
latest_qr = None
#bridge = CvBridge()


def local_position_callback(data):
    global local_position
    local_position = data
    #print("#### local_position_callback updated ###", local_position)

#def image_callback(data):
#    try:
#        cv_image = bridge.imgmsg_to_cv2(data, "bgr8")
#    except CvBridgeError as e:
#        rospy.logerr(e)
#        return

#    result_image, detection = process_image(cv_image)

#    if detection:
#        rospy.loginfo("H detected at: %s", detection)
        # this is for land
#        setLandMode()

#    try:
#        self.image_pub.publish(bridge.cv2_to_imgmsg(result_image, "bgr8"))
#    except CvBridgeError as e:
#       rospy.logerr(e)

def process_image(cv_image):
    hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) == 12:  # Assuming H shape approximates to 12 points
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(cv_image, "H", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            return cv_image, (x, y, w, h)

    return cv_image, None

set_point_pub = rospy.Publisher("/mavros/setpoint_position/local", PoseStamped, queue_size=10)
rospy.Subscriber("/mavros/vision_pose/pose", PoseStamped, local_position_callback)
#rospy.Subscriber('/camera_1', Image, image_callback)
pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped, queue_size=10)

def call_set_mode(mode, mode_ID):
    try:
        service = rospy.ServiceProxy("/mavros/set_mode", SetMode)
        rospy.wait_for_service("/mavros/set_mode")
        print(service(mode_ID, mode))
    except rospy.ServiceException as e:
        print('Service call failed: %s' % e)

def pub_reset_gps():
    msg = GeoPointStamped()
    reset_gps = rospy.Publisher("/mavros/global_position/set_gp_origin", GeoPointStamped, queue_size=10)
    for _ in range (0,5):
        try:
            reset_gps.publish(msg)
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

def setGuidedNoGPSMode():
    rospy.wait_for_service('/mavros/set_mode')
    try:
        flightModeService = rospy.ServiceProxy('/mavros/set_mode', mavros_msgs.srv.SetMode)
        isModeChanged = flightModeService(custom_mode='GUIDED_NOGPS') #return true or false
    except rospy.ServiceException as e:
        print("service set_mode call failed: %s. GUIDED_NOGPS Mode could not be set. Check that GPS is enabled" % e)

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

def setArm():
    # pub_reset_gps()
    # time.sleep(1)
    rospy.wait_for_service('/mavros/cmd/arming')
    try:
        # TODO this is to verify why the drone is arming but not launching
        # rospy.set_param("/mavros/vision_pose/tf/listen", True)
        # pub_reset_gps()

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
        takeoffService(altitude = 1.0, latitude = 0, longitude = 0, min_pitch = 0, yaw = 0)
    except rospy.ServiceException as e:
        print("Service takeoff call failed: %s" % e)

def takeoff_guided_nogps(target_altitude_m=1.0, climb_speed=0.3):
    rate = rospy.Rate(10)  # 10 Hz

    twist = TwistStamped()
    twist.twist.linear.x = 0.0
    twist.twist.linear.y = 0.0
    twist.twist.linear.z = -abs(climb_speed)  # subir
    ### odometria de zed?
    duration = target_altitude_m / climb_speed # se puede poner por 0.5 segundos
    rospy.loginfo(f"Subiendo {target_altitude_m} metros a velocidad {climb_speed} m/s (duración: {duration} s)")
    
    start_time = rospy.Time.now()
    while rospy.Time.now() - start_time < rospy.Duration(duration) and not rospy.is_shutdown():
        twist.header.stamp = rospy.Time.now()
        pub.publish(twist)
        rate.sleep()

    # Detener ascenso
    twist.twist.linear.z = 0.0
    twist.header.stamp = rospy.Time.now()
    pub.publish(twist)

    rospy.loginfo("Takeoff completado")

def land_guided_nogps(land_time=5, descend_speed=0.3):
    rate = rospy.Rate(10)  # 10 Hz

    twist = TwistStamped()
    twist.twist.linear.x = 0.0
    twist.twist.linear.y = 0.0
    twist.twist.linear.z = descend_speed  # +Z es bajar
    
    start_time = rospy.Time.now()
    duration = rospy.Duration(land_time)  # bajar por 5 segundos

    rospy.loginfo("Iniciando aterrizaje guiado sin GPS")
    while rospy.Time.now() - start_time < duration and not rospy.is_shutdown():
        twist.header.stamp = rospy.Time.now()
        pub.publish(twist)
        rate.sleep()

    # Detener movimiento vertical
    twist.twist.linear.z = 0.0
    twist.header.stamp = rospy.Time.now()
    pub.publish(twist)

    rospy.loginfo("Aterrizaje completado")

def globalPositionCallback(globalPositionCallback):
    global latitude
    global longitude
    latitude = globalPositionCallback.latitude
    longitude = globalPositionCallback.longitude
    #print ("longitude: %.7f" %longitude)
    #print ("latitude: %.7f" %latitude)

def move_xyz(dx=0.0, dy=0.0, dz=0.0, speed=0.5):
    rate = rospy.Rate(10)  # 10 Hz

     # Calcular distancia total (módulo del vector)
    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    if distance == 0:
        rospy.logwarn("No se indicó distancia a mover.")
        return

    duration = distance / speed
    start_time = time.time()

    # Calcular velocidades proporcionales en cada eje para mantener dirección
    vx = (dx / distance) * speed
    vy = (dy / distance) * speed
    vz = (dz / distance) * speed

    move_cmd = Twist()
    move_cmd.linear.x = vx
    move_cmd.linear.y = vy
    move_cmd.linear.z = vz
    move_cmd.angular.x = 0
    move_cmd.angular.y = 0
    move_cmd.angular.z = 0

    rospy.loginfo(f"Moviendo: dx={dx} m, dy={dy} m, dz={dz} m a velocidad {speed} m/s durante {duration:.2f} s")

    while time.time() - start_time < duration and not rospy.is_shutdown():
        pub.publish(move_cmd)
        rate.sleep()

    # Detener el dron
    stop_cmd = Twist()
    pub.publish(stop_cmd)
    rospy.loginfo("Movimiento completado y detenido.")

def set_target_position(what, x,y,z=0.0,w=0.0):
    global pose
    pose_local = PoseStamped()
    #pose.pose.position.x = x
    #pose.pose.position.y = y
    #pose.pose.position.z = z
    #pose.pose.orientation.x = 0
    #pose.pose.orientation.y = 0
    #pose.pose.orientation.z = 0
    #pose.pose.orientation.w = w
    step_x = 0
    step_y = 0

    pose_local.pose.position.x = what.pose.position.x
    pose_local.pose.position.y = what.pose.position.y
    #print(pose_local)
    try:
        distance_x = pose_local.pose.position.x - x
        distance_y = pose_local.pose.position.y - y
        print("distance")
        print(distance_x, distance_y)
        print("---------")
        try:
              while not rospy.is_shutdown():
                   if distance_x < -0.1: step_x = 0.1
                   elif distance_x > 0.1: step_x = -0.1
                   else: step_x = 0.0

                   if distance_y < -0.1: step_y = 0.1
                   elif distance_y > 0.1: step_y = -0.1
                   else: step_y = 0.0

                   pose_local.pose.position.x = pose_local.pose.position.x + step_x
                   pose_local.pose.position.y = pose_local.pose.position.y + step_y
                   print(pose_local.pose.position.x, pose_local.pose.position.y)
                   if((abs(pose_local.pose.position.x - x) < 0.15) and (abs(pose_local.pose.position.y - y) < 0.15)):
                        break

                   try:
                        qr_detected = rospy.wait_for_message('/qrcode/raw', String, timeout=1.0)
                        print("QR not detected")
                        break
                   except:
                        pass
                   try:
                        set_point_pub.publish(pose_local)
                        time.sleep(1)
                   except KeyboardInterrupt:
                        setLandMode()
                        print("Shutting down")
              base_pose = pose_local
        except KeyboardInterrupt:
              setLandMode()
              print("Shutting down")

    except rospy.ServiceException as e:
        print("Service set_target_position call failed: %s" % e)

def follow_line():
    pass

def string_to_pose(input_string):
    global mission
    global pose
    global distanceQRx
    global distanceQRy
    #print("#### input_string  ###", input_string)
    #TODO replace data from string 
    parts = str(input_string).replace('data: ', '').replace('"', '').split(',')

    print("#### parts ###", parts)
    if len(parts) != 5:
        raise ValueError("Input string should have 5 comma-separated values")
    if (parts[-1] == '0'):
        # Asignar la orientacion basada en la direccion de la secuencia
        if parts[mission-1] == 'N':
            pose.pose.position.x += distanceQRx
            pose.pose.position.y += 0.0
        elif parts[mission-1] == 'E':
            pose.pose.position.x += 0.0
            pose.pose.position.y += -distanceQRy
        elif parts[mission-1] == 'S':
            pose.pose.position.x += -distanceQRx
            pose.pose.position.y += 0.0
        elif parts[mission-1] == 'W':
            pose.pose.position.x += 0.0
            pose.pose.position.y += distanceQRy

        #rospy.loginfo("string_to_pose -> %s" % pose)
        # Asignar el numero de posicion objetivo
        #pose.header.stamp = rospy.Time.now()
        #pose.header.frame_id = 'map'  # Ajustar el frame_id segun sea necesario
        #pose.pose.position.z = float(parts[4])

        return pose, parts[4]

def go_to_destination(dest = "1.0, 0.0, 1.0, 0.0"):        
    x, y, z, w = dest.split(",")
    rospy.set_param("/mavros/vision_pose/tf/listen", True)
    setGuidedNoGPSMode()
    # time.sleep(1)
    #pub_reset_gps()
    # time.sleep(1)
    time.sleep(5)
    setArm()
    time.sleep(1)
    takeoff_guided_nogps()
    time.sleep(5)
    # set_target_position(x, y, z, w)
    move_xyz(x, y, z, w)
    time.sleep(1)
    land_guided_nogps()
    time.sleep(1)
    setDisarm()

def read_qr_and_go_to_destination(direction):
    global mission
    global pose
    global local_position
    global target_flag
    global latest_qr
    global altitude
    global distanceQRx
    global distanceQRy
    global base_pose
    mission = 1
    try:
        if (local_position != None):
            time.sleep(1)
            setGuidedMode()
            rospy.loginfo("Setou")
            time.sleep(1)
            rospy.set_param("/mavros/vision_pose/tf/listen", True)
            time.sleep(1)
            pub_reset_gps()
            pub_reset_gps()
            rospy.loginfo("Fake gps")
            time.sleep(5)
            setArm()
            time.sleep(1)
            setArm()
            rospy.loginfo("armou")
            time.sleep(1)
            setTakeoffMode()
            rospy.loginfo("take off")
            time.sleep(5)
            # 1 meter to the rgight
            print("### GET OVER THE QR CODE")
            base_pose.pose.position.x = 0
            base_pose.pose.position.y = 0
            #set_target_position(base_pose, 0.0, -2.2, 0.0)
            if(direction == 'right'):
                  set_target_position(base_pose, 0.0, -8.0, 0.0)
            else:
                  set_target_position(base_pose, 0.0, 8.0, 0.0)
            #set_target_position(0.0,1.0,0.0)
            time.sleep(1.5)
            #base_pose.pose.position.x = 0
            #base_pose.pose.position.y = -7.2

            #set_target_position(base_pose, 1.25, -7.2, 0.0)
            #time.sleep(1.5)
            #print("Going down")
            #set_target_position(distanceQRx, 0.0, -0.5)
            # set_target_position(0.0, 2.0, 0.0)
            #time.sleep(10)
            # set_target_position(0.0, 3.0, 0.0)
            # time.sleep(5)


            while True:
                rospy.loginfo("### WHILE ###")
                try:
                    qr_detected = rospy.wait_for_message('/qrcode/raw', String, timeout=10)
                except:
                    qr_detected = None
                    rospy.loginfo("### Exception on QR_DETECTED ###")
                    break

                if(qr_detected):
                    latest_qr = qr_detected
                    print("QR Code detected", qr_detected)
                    print("#### BASE POSITION BEFORE ->", base_pose.pose.position.x, base_pose.pose.position.y)
                    #rospy.loginfo("QR Code detected", qr_detected)
                    pose, target_flag = string_to_pose(qr_detected)
                else:
                    rospy.loginfo("QR Code not detected")
                    # setLandMode()
                break
                print("#### BASE POSITION ->", base_pose.pose.position.x, base_pose.pose.position.y)
                print("#### GOING NEXT POSITION ->", pose.pose.position.x, pose.pose.position.y)
                set_target_position(base_pose, pose.pose.position.x, pose.pose.position.y)
                base_pose = pose
                #print("#### pose ->", pose)
                #print("#### GOING NEXT POSITION ->", pose.pose.position.x, pose.pose.position.y)
                #time.sleep(10)

                if (target_flag == 1): mission = 2
                if (target_flag == 2): mission = 3
                if (target_flag == 3): mission = 4
                if (target_flag == 4): break

            # read qr codes with node.
            new_pose = PoseStamped()
            new_pose.pose.position.x = 0
            new_pose.pose.position.y = -7.2
            time.sleep(5)
            try:
                qr_detected = rospy.wait_for_message('/qrcode/raw', String, timeout=10)
            except:
                qr_detected = None
                setLandMode()
                rospy.loginfo("### Exception on QR_DETECTED ###")

            set_target_position(new_pose, 1.25, -7.2)
            time.sleep(1.5)
            try:
                qr_detected = rospy.wait_for_message('/qrcode/raw', String, timeout=10)
            except:
                qr_detected = None
                rospy.loginfo("### Exception on QR_DETECTED ###")

            setLandMode()
    except rospy.ServiceException as e:
        rospy.loginfo("Exception read_qr_and_go_to_destination", e)
        setLandMode()

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
    print("11: Read QR-Codes L")

def myLoop():
    x='1'
    while ((not rospy.is_shutdown())and (x in ['1','2','3','4','5','6','7','8','9', '10'])):
        menu()
        x = input("Enter your input: ")
        if (x=='1'):
            setGuidedMode()
        elif(x=='2'):
            setStabilizeMode()
        elif(x=='3'):
            setArm()
        elif(x=='4'):
            setDisarm()
        elif(x=='5'):
            setTakeoffMode()
        elif(x=='6'):
            setLandMode()
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
            read_qr_and_go_to_destination("right")
        elif(x=='10'):
            pub_reset_gps()
        elif(x=='11'):
            read_qr_and_go_to_destination("left")
        else:
            print("Exit")


if __name__ == '__main__':
    try:
        rospy.init_node('uav_mission_planner', anonymous=True)
        rospy.Subscriber("/mavros/global_position/raw/fix", NavSatFix, globalPositionCallback)
        # state = rospy.Subscriber('/mavros/state', State, state_callback)
        # TODO check with subscription to state
        myLoop()
        # rospy.spin()
    except rospy.ROSInterruptException:
        setLandMode()
        rospy.loginfo("#### Exception uav ####")