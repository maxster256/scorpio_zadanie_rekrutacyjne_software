#!/usr/bin/env python3
import rospy
from autonomy_simulator.msg import SetGoal, RoverPose
from std_msgs.msg import UInt8
from path_planning import find_path

moves_sequence = []
current_x = current_y = current_orientation = 0
bool_find_path = bool_pose = False

def goal_callback(msg: SetGoal):
    global goal_x, goal_y, bool_find_path
    goal_x = int(msg.x)
    goal_y = int(msg.y)
    rospy.loginfo(f"x: {msg.x}, y: {msg.y}")
    bool_find_path = True
    # flaga do zapewnienia ze sekwencja ruchow nie bedzie tworzona przed uzyskaniem wspolrzednych celu

def pose_callback(msg: RoverPose):
    global current_x, current_y, current_orientation, bool_pose
    current_orientation = int(msg.orientation)
    current_x = int(msg.x)
    current_y = int(msg.y)
    rospy.loginfo(f"x: {msg.x}, y: {msg.y}, orientation: {msg.orientation}")


if __name__ == '__main__':
    rospy.init_node("set_goal_subscriber")
    move_pub = rospy.Publisher("/rover/move", UInt8, queue_size = 10)
    goal_sub = rospy.Subscriber("/set_goal", SetGoal, callback=goal_callback)
    pose_sub = rospy.Subscriber("/rover/pose", RoverPose, callback=pose_callback)
    rospy.Rate(2).sleep()
    rospy.loginfo("The node has started")

    while not rospy.is_shutdown():
        while not bool_find_path:
            pass
        msg_to_pub = UInt8()
        rate = rospy.Rate(5)

        moves_sequence = find_path(goal_x, goal_y, current_x, current_y, current_orientation)

        for move in moves_sequence:
            msg_to_pub.data = move
            move_pub.publish(msg_to_pub)
            rate.sleep()
        
        moves_sequence.clear()
        bool_find_path = False