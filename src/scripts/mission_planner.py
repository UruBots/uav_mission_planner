#!/usr/bin/env python

import rospy
from status import Status
from mavros_controller import MavrosController
from object_detector import ObjectDetector
from qr_code_detector import QrDetector
from line_follower import LineFollower
from std_msgs.msg import String

class MissionController(object):
	def __init__(self):
		rospy.init_node('mission_controller', anonymous=True)
		# self.qr_detector = QrDetector()
		# self.detector = ObjectDetector()
		self.controller = MavrosController()
		# self.line_follower = LineFollower()
  		# drone status -1 notinited , 1 inited, 2 landed, 3 flying
		self.status = Status.NotInited
  		# Parameters
		self.type = rospy.get_param('type', 1)
		# ODOMETRY

	def drive(self):
		print("start mission")
		print("type: ", self.type)
		if self.type == 1:
			self.task()
		elif self.type == 2:
			self.task_two()
		else:
			pass
    
	def task(self):
		while not rospy.is_shutdown():
        	# sleep 1 second to wait the drone initial
			rate = rospy.Rate(1)
			rate.sleep()
			if self.status == Status.NotInited:
				print("send take off")
				self.controller.fly_drone()
				self.status = 1
				self.controller.set_status = self.status
			elif self.status == Status.Inited:
				print("send go foward")
				# self.controller.set_target_position(x = 0.5, y = 0, z = 0, w = 0)
				self.status = Status.Flying
			elif self.status == Status.Flying:
				# qr code
				try:
					message = rospy.wait_for_message('/qrcode/raw', String, timeout=5)
				except:
					message = None
				print("QR message: ", message)
				# position = rospy.wait_for_message('/mavros/raw', String, timeout=5)
			else:
				pass
		# land drone
		print("send land")
		self.controller.land_drone()


	def task_two(self):
		return 0

if __name__=='__main__':
	auto_drive = MissionController()
	auto_drive.drive()
        