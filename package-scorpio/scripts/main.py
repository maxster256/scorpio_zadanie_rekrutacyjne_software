#!/usr/bin/env python3
import sys
import rospy
from autonomy_simulator.msg import SetGoal, RoverPose
from std_msgs.msg import UInt8
from autonomy_simulator.srv import GetMap
from path_planning import find_path

moves_sequence = []
current_x = current_y = current_orientation = 0
bool_find_path = bool_pose = False

def get_map_service():
    global mapData
    try:
        get_map = rospy.ServiceProxy("/get_map", GetMap)
        mapData = get_map().data
        #rospy.loginfo(mapData)
    except rospy.ServiceException as e:
        rospy.logwarn(e)

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
    rospy.loginfo(f"x: {msg.x}, y: {msg.y}, orientation: {msg.orientation}, height: {mapData[msg.x + msg.y * 50]}")

def displaymMap(mapData):
    for i in range(0, len(mapData)):
        if i%25 == 0:
            print(f"row: {i//50:<2}, ",end=" ")
            if i%2 == 0:
                print(f"columns: 0--24, ",end=" ")
            else:
                print(f"columns: 25-49, ",end=" ")
        elif i%25 != 24:
            print(f"{mapData[i]:<3}", end=" ")
        else:
            print(f"{mapData[i]:<3}")

if __name__ == '__main__':
    rospy.init_node("set_goal_subscriber")
    rospy.wait_for_service("/get_map")
    get_map_service()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "1": # wyswietlenie mapy po podaniu argumentu '1'
            displaymMap(mapData)

    goal_sub = rospy.Subscriber("/set_goal", SetGoal, callback=goal_callback)
    pose_sub = rospy.Subscriber("/rover/pose", RoverPose, callback=pose_callback)
    move_pub = rospy.Publisher("/rover/move", UInt8, queue_size=10)
    rospy.loginfo("The node has started")

    while not rospy.is_shutdown():
        while not bool_find_path:
            pass
        moves_sequence = find_path(goal_x, goal_y, current_x, current_y, current_orientation, mapData)
        
        msg_to_pub = UInt8()
        rate = rospy.Rate(5)

        for move in moves_sequence:
            rate.sleep()
            msg_to_pub.data = move
            move_pub.publish(msg_to_pub)
        
        moves_sequence.clear()
        bool_find_path = False
