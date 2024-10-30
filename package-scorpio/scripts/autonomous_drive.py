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

    if current_x != goal_x or current_y != goal_y:
        rospy.loginfo(f"x: {msg.x}, y: {msg.y}, orientation: {msg.orientation}")
        msg_to_pub = UInt8()
        msg_to_pub.data = 2
        if current_x < goal_x: #cel na prawo
            if msg.orientation != 1:
                msg_to_pub.data = 1

        elif current_x > goal_x: #cel na lewo
            if msg.orientation != 3:
                msg_to_pub.data = 1

        elif current_y < goal_y: # cel u gory
            if msg.orientation != 0:
                msg_to_pub.data = 1
            
        else:                   # cel u dolu
            if msg.orientation != 2:
                msg_to_pub.data = 1

        move_pub.publish(msg_to_pub)
    else:
        rospy.loginfo(f"Reached position x: {msg.x}, y: {msg.y}. Waiting...")
        

if __name__ == '__main__':
    rospy.init_node("set_goal_subscriber")
    goal_sub = rospy.Subscriber("/set_goal", SetGoal, callback=goal_callback)
    pose_sub = rospy.Subscriber("/rover/pose", RoverPose, callback=pose_callback)
    
    move_pub = rospy.Publisher("/rover/move", UInt8, queue_size = 10)
    
    rospy.loginfo("The node has started")

    rospy.spin()
