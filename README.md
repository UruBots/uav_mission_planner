# uav_mission_planner ROS2 Foxy
This repository contains the code that will be used on WORLD FIRA for UAV competition.

### Dependencies
- zed_wrapper - https://github.com/stereolabs/zed-ros2-wrapper
- zed-sdk - https://download.stereolabs.com/zedsdk/4.2/l4t32.7/jetsons?_gl=1*vyuivg*_gcl_au*MjA5MjQ0Njg1Ni4xNzQ1ODU2NzE0

### Install
In your worspace execute:
```
source install/setup.bash
colcon build
```

### Usage
* Launch: Execute launchers fo PX4, camera and the remaping of the topics.  
```
ros2 launch uav_mission_planner launch.launch.py
```
* Mission Planner: Execute the mission planner menu.
```
ros2 launch uav_mission_planner uav_mission_planner.launch.py
```