#!/usr/bin/env python
#import curses #for terminal interface
import math
import time
import random

import rospy
from actionlib import SimpleActionClient, GoalStatus
from play_motion_msgs.msg import PlayMotionAction, PlayMotionGoal
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Twist, PoseStamped
from pal_detection_msgs.msg import Detections2d

class SimpleDance():
    def __init__(self):
        self._hz = rospy.get_param('~hz', 10)
	self._rate = rospy.Rate(self._hz)
	self._is_moving = True

	self._pub = rospy.Publisher('key_vel', Twist, queue_size=10)
	random.seed()

    def _get_twist(self, linear, angular):
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angular
        return twist

    def _wave(self):
	client = SimpleActionClient('/play_motion', PlayMotionAction)
	client.wait_for_server()

	goal = PlayMotionGoal()
	goal.motion_name = 'wave'
	client.send_goal(goal)
	action_ok = client.wait_for_result(rospy.Duration(30.0))
#	state = client.get_state()
	return client.get_result()


    def move_circle(self):
	pub = rospy.Publisher('key_vel', Twist, queue_size=10)
        for j in range(115):
		move = self._get_twist(0.75, math.radians(36))
		pub.publish(move)
		self._rate.sleep()
	rospy.spin()



    def goal_pose(self, pose):
	
	pub = rospy.Publisher("/move_base_simple/goal", PoseStamped, queue_size=10)
	msg = PoseStamped()
	msg.pose.position.x = 2
	msg.pose.position.y = 4
	pub.publish(msg)
	while not rospy.is_shutdown():
	    pub.publish(msg)
	    self._rate.sleep()
#	client = SimpleActionClient('/move_base', MoveBaseAction)
#	client.wait_for_server()
#	goal_pose = MoveBaseGoal()
#	goal_pose.target_pose.header.frame_id = 'map'
#	goal_pose.target_pose.pose.position.x = 2
#	goal_pose.target_pose.pose.position.y = 4
#	client.send_goal(goal_pose)

    def _random_walk(self):
	while self._is_moving:
	    linear = random.random()
	    angular = random.gauss(0,90)
	    move = self._get_twist(linear, math.radians(angular))
	    self._pub.publish(move)
	    self._rate.sleep()


    def _person_detected(self, data):
	print(str(len(data.detections)) + "\n\n")
	print(data.detections)
	if len(data.detections) > 0 :
	    self._is_moving = False
	else:
	    self._is_moving = True
	
    def _turn_around(self):
	for j in range(60):
		move = self._get_twist(0.0, math.radians(36))
		self._pub.publish(move)
		self._rate.sleep()

    def main_fun(self):
	rospy.Subscriber("/person_detector/detections", Detections2d, self._person_detected)
	while not rospy.is_shutdown():
	    self._random_walk()
	    if self._is_moving == False:
		msg = None
		try:
		    msg = rospy.wait_for_message("texture_detector/pose", PoseStamped, timeout=4)
		except:
		    pass
	        if msg is not None:
		    self._wave()
		    self._turn_around()
		else:
		    self._is_moving = True
#	rospy.spin()

    def dance(self):
	pass


def main():
    rospy.init_node('ari_says_hi')
    app = SimpleDance()
    app.main_fun()
#    app.wave()
#    app.move_circle()
#    app.dance()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass