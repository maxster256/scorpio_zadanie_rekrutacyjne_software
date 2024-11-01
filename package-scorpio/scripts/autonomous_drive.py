#!/usr/bin/env python3
import rospy
from autonomy_simulator.msg import SetGoal, RoverPose
from std_msgs.msg import UInt8

moves_sequence = []
current_x = current_y = current_orientation = 0
bool_find_path = False

def goal_callback(msg: SetGoal):
    global goal_x, goal_y, bool_find_path
    goal_x = int(msg.x)
    goal_y = int(msg.y)
    rospy.loginfo(f"x: {msg.x}, y: {msg.y}")
    bool_find_path = True
    # flaga do zapewnienia ze sekwencja ruchow nie bedzie tworzona przed uzyskaniem wspolrzednych celu

def pose_callback(msg: RoverPose):
    global current_x, current_y, current_orientation
    current_orientation = int(msg.orientation)
    current_x = int(msg.x)
    current_y = int(msg.y)
    rospy.loginfo(f"x: {msg.x}, y: {msg.y}, orientation: {msg.orientation}")

# funkcja dodajaca ruchy w przod lub w tyl w zaleznosci od polozenia celu
def append_moves(goal, current_position):
    if current_position < goal:
        for i in range(goal-current_position):
            moves_sequence.append(2)
    else:
        for i in range(current_position-goal):
             moves_sequence.append(3)


# przyjete w tym kodzie do tego zadania jest, ze lazik zawsze jest obrocony w kierunku
# polnocnym lub wschodnim
def find_path():
    if current_orientation == 0: # odwrocony w gore
        append_moves(goal_y, current_y)
        moves_sequence.append(1)
        append_moves(goal_x, current_x)

    else:                       # odwrocony w prawo
        append_moves(goal_x, current_x)
        moves_sequence.append(0)
        append_moves(goal_y, current_y)


if __name__ == '__main__':
    rospy.init_node("set_goal_subscriber")
    goal_sub = rospy.Subscriber("/set_goal", SetGoal, callback=goal_callback)
    pose_sub = rospy.Subscriber("/rover/pose", RoverPose, callback=pose_callback)
    move_pub = rospy.Publisher("/rover/move", UInt8, queue_size = 10)
    rospy.loginfo("The node has started")

    while not rospy.is_shutdown():
        while not bool_find_path:
            pass
        find_path()

        msg_to_pub = UInt8()

        rate = rospy.Rate(5)
        for move in moves_sequence:
            msg_to_pub.data = move
            move_pub.publish(msg_to_pub)
            rate.sleep()
        
        moves_sequence.clear()
        bool_find_path = False
