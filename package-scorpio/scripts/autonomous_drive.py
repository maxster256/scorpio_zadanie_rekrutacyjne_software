#!/usr/bin/env python3
import rospy
from autonomy_simulator.msg import SetGoal, RoverPose
from std_msgs.msg import UInt8

def goal_callback(msg: SetGoal):
    global goal_x, goal_y
    goal_x = int(msg.x)
    goal_y = int(msg.y)
    rospy.loginfo(f"x: {msg.x}, y: {msg.y}")

def pose_callback(msg: RoverPose):
    global current_x, current_y
    current_x = int(msg.x)
    current_y = int(msg.y)
    rospy.loginfo(f"x: {msg.x}, y: {msg.y}, orientation: {msg.orientation}")

if __name__ == '__main__':
    rospy.init_node("set_goal_subscriber")
    goal_sub = rospy.Subscriber("/set_goal", SetGoal, callback=goal_callback)
    pose_sub = rospy.Subscriber("/rover/pose", RoverPose, callback=pose_callback)
    
    move_pub = rospy.Publisher("/rover/move", UInt8, queue_size = 10)
    
    rospy.loginfo("The node has started")

    rate = rospy.Rate(5)
    rate.sleep()
    msg = UInt8()
    msg.data = 2 #ruch do przodu powtarzany w petli
    while current_y < goal_y:
        move_pub.publish(msg)
        rate.sleep()
    
    msg.data = 1 #jednorazowy obrot w prawo
    move_pub.publish(msg)
    rate.sleep()
    msg.data = 2 #ruch do przodu powtarzany w petli

    while current_x < goal_x:
        move_pub.publish(msg)
        rate.sleep()

    rospy.loginfo(f"Reached position x: {current_x}, y: {current_y}")