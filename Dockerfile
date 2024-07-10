FROM osrf/ros:noetic-desktop-full
# ARG USER=user
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /home/drone
# Install dependencies
SHELL ["/bin/bash", "-c"]
RUN apt-get update  && apt-get dist-upgrade -y && apt-get install -y \
    curl git libgl1-mesa-glx mesa-utils python3 python3-pip && \
    # python3-rosdep python3-rosinstall python3-rosinstall-generator && \ 
    # python3-wstool build-essential && \
    rm -rf /var/lib/apt/lists/*
# Install gazebo
RUN curl -sSL http://get.gazebosim.org | bash
RUN source /opt/ros/${ROS_DISTRO}/setup.bash
# Create workspace
RUN mkdir -p /home/drone/catkin_ws/src && \
    cd /home/drone/catkin_ws/src && \
    source /opt/ros/noetic/setup.bash && \
    catkin_init_workspace && \
    cd /home/drone/catkin_ws && \
    catkin_make
RUN curl https://ctu-mrs.github.io/ppa-stable/add_ppa.sh | bash
RUN apt-get update && apt-get install -y ros-noetic-mrs-uav-system-full
RUN source /opt/ros/${ROS_DISTRO}/setup.bash
# RUN roscd mrs_uav_gazebo_simulation/tmux/one_drone && ./start.sh