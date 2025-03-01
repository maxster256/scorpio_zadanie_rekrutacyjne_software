#!/usr/bin/env python3
import rospy
from autonomy_simulator.msg import SetGoal, RoverPose
from std_msgs.msg import UInt8

if __name__ == '__main__':
    rospy.logwarn("The main module is main.py!")

# funkcja dodajaca ruchy w przod lub w tyl w zaleznosci od polozenia celu
def append_moves(goal, current_position, moves):
    if current_position < goal:
        for i in range(goal-current_position):
            moves.append(2)
    else:
        for i in range(current_position-goal):
            moves.append(3)


# przyjete w tym kodzie do tego zadania jest, ze lazik zawsze jest obrocony w kierunku
# polnocnym lub wschodnim
def find_path(goal_x, goal_y, current_x, current_y, current_orientation):
    moves_sequence = []
    if current_orientation == 0: # odwrocony w gore
        append_moves(goal_y, current_y, moves_sequence)
        moves_sequence.append(1)
        append_moves(goal_x, current_x, moves_sequence)

    else:                       # odwrocony w prawo
        append_moves(goal_x, current_x, moves_sequence)
        moves_sequence.append(0)
        append_moves(goal_y, current_y, moves_sequence)
    return moves_sequence