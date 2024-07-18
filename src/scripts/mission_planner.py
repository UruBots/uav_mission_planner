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
		self.qr_detector = QrDetector()
		self.detector = ObjectDetector()
		self.controller = MavrosController()
		self.line_follower = LineFollower()
		self.status = Status.NotInited # drone status , 0 flying, -1 landed
		# ODOMETRIA

  
	def drive(self, option):
		if option == 1:
			self.task()
		elif option == 2:
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
				self.controller.start_drone()
				self.status = 1
				self.controller.set_status = self.status
			elif self.status == Status.Inited:
				print("send go foward")
				self.controller.set_target_position(x = 0.5, y = 0, z = 0, w = 0)
				self.status = Status.Flying
			elif self.status == Status.Flying:
				# qr code		
				print(rospy.wait_for_message('/qrcode/raw', String, timeout=5))
			else:
				pass
		self.controller.Land()


	def task_two(self):
		return 0

if __name__=='__main__':
	auto_drive = MissionController()
	auto_drive.drive()
        