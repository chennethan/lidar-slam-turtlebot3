#!/bin/bash
pkill -f gz
pkill -f ros2
pkill -f rviz
pkill -f gazebo
echo "All ROS2/Gazebo processes killed."
