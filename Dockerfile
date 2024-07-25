FROM osrf/ros:noetic-desktop-full
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /home/drone
# Install dependencies
SHELL ["/bin/bash", "-c"]
RUN apt-get update  && apt-get dist-upgrade -y && apt-get install -y \
    curl wget git cmake libgl1-mesa-glx mesa-utils python3 python3-pip && \
    # nvidia-cuda-toolkit
    rm -rf /var/lib/apt/lists/*   

# Install gazebo
RUN curl -sSL http://get.gazebosim.org | bash
RUN source /opt/ros/${ROS_DISTRO}/setup.bash
 
# Mavros
RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
RUN apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
RUN apt update
RUN apt-get install ros-noetic-mavros ros-noetic-mavros-extras -y
# Mavros geographic dataset
RUN wget https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh
RUN chmod a+x install_geographiclib_datasets.sh
RUN ./install_geographiclib_datasets.sh

# MRS
RUN curl https://ctu-mrs.github.io/ppa-stable/add_ppa.sh | bash
RUN apt-get update && apt-get install -y \
    ros-noetic-mrs-uav-system-full \
    ros-noetic-mrs-uav-gazebo-simulation \
    ros-noetic-mrs-uav-px4-api \
    ros-noetic-mrs-multirotor-simulator

# Create workspace
RUN source /opt/ros/noetic/setup.bash && \ 
    mkdir -p /home/drone/catkin_ws && \
    mkdir -p /home/drone/catkin_ws/src && \
    mkdir -p /home/drone/catkin_ws/src/uav_mission_planner && \
    cd /home/drone/catkin_ws && \
    # catkin_init_workspace && \
    catkin_make

# UAV
ADD ./uav_mission_planner /home/drone/catkin_ws/src/uav_mission_planner

RUN source /opt/ros/noetic/setup.bash && \
    cd /home/drone/catkin_ws && \
    catkin_make

RUN cd /home/drone/catkin_ws/src/uav_mission_planner && pip install -r requirements.txt
RUN source /home/drone/catkin_ws/devel/setup.bash 
# && roslaunch mrs_uav_gazebo_simulation simulation.launch world_name:=grass_plane gui:=true
