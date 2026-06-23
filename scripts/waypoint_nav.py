#!/usr/bin/env python3

import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped

def make_pose(nav, x, y, yaw_z=0.0, yaw_w=1.0):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = nav.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = yaw_z
    pose.pose.orientation.w = yaw_w
    return pose

def main():
    rclpy.init()
    nav = BasicNavigator()

    nav.waitUntilNav2Active()

    waypoints = [
        make_pose(nav, 2.01,  -1.28),
        make_pose(nav, 2.59,  -0.0491),
        make_pose(nav, 1.59,   1.09),
        make_pose(nav, 2.64,   2.25),
        make_pose(nav, 0.132,  1.04),
    ]

    nav.followWaypoints(waypoints)

    while not nav.isTaskComplete():
        feedback = nav.getFeedback()
        if feedback:
            wp = feedback.current_waypoint
            print(f'Navigating to waypoint {wp + 1} / {len(waypoints)}')

    result = nav.getResult()
    if result == TaskResult.SUCCEEDED:
        print('All waypoints reached successfully.')
    elif result == TaskResult.CANCELED:
        print('Navigation was canceled.')
    elif result == TaskResult.FAILED:
        print(f'Navigation failed at waypoint {feedback.current_waypoint + 1}.')

    nav.lifecycleShutdown()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
