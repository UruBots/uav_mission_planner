FROM osrf/ros:noetic-desktop-full
# ARG USER=user
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /home/drone
# Install dependencies
SHELL ["/bin/bash", "-c"]
RUN apt-get update  && apt-get dist-upgrade -y && apt-get install -y \
    curl wget git cmake libgl1-mesa-glx mesa-utils python3 python3-pip \
    zstd nvidia-cuda-toolkit && \
    rm -rf /var/lib/apt/lists/*

# Install gazebo
RUN curl -sSL http://get.gazebosim.org | bash
RUN source /opt/ros/${ROS_DISTRO}/setup.bash

# PX4
RUN git clone https://github.com/PX4/Firmware.git --recursive
RUN cd /home/drone/Firmware && chmod +x /home/drone/Firmware/Tools/setup/ubuntu.sh && cd /home/drone/Firmware/Tools/setup/ && ./ubuntu.sh
# RUN cd /home/drone/Firmware
# RUN git submodule update --init --recursive
RUN DONT_RUN=1 make px4_sitl_default gazebo
RUN source /home/drone/Firmware/Tools/simulation/gazebo/setup_gazebo.bash $(pwd) $(pwd)/build/px4_sitl_default
RUN export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:$(pwd):$(pwd)/Tools/simulation/gazebo/sitl_gazebo
RUN roslaunch px4 multi_uav_mavros_sitl.launch

# Mavros
RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
RUN apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
RUN apt update
RUN apt-get install ros-noetic-mavros ros-noetic-mavros-extras -y
# Mavros geographic dataset
RUN wget https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh
RUN chmod a+x install_geographiclib_datasets.sh
RUN ./install_geographiclib_datasets.sh

# Create workspace
RUN mkdir -p /home/drone/catkin_ws/src && \
    cd /home/drone/catkin_ws/src && \
    source /opt/ros/noetic/setup.bash && \
    catkin_init_workspace && \
    cd /home/drone/catkin_ws && \
    catkin_make

# Camera
RUN wget https://stereolabs.sfo2.cdn.digitaloceanspaces.com/zedsdk/4.1/ZED_SDK_Ubuntu20_cuda11.8_v4.1.3.zstd.run
RUN chmod +x ZED_SDK_Ubuntu20_cuda11.8_v4.1.3.zstd.run; ./ZED_SDK_Ubuntu20_cuda11.8_v4.1.3.zstd.run -- silent skip_tools skip_cuda
RUN cd /home/drone/catkin_ws/src && git clone --recursive https://github.com/stereolabs/zed-ros-wrapper.git
RUN cd /home/drone/catkin_ws && rosdep install --from-paths src --ignore-src -r -y
RUN cd /home/drone/catkin_ws && source ./devel/setup.bash && catkin_make -DCMAKE_BUILD_TYPE=Release 

# UAV
COPY uav_mission_planner /home/drone/catkin_ws/src
RUN source /opt/ros/noetic/setup.bash && \
    cd /home/drone/catkin_ws && \
    catkin_make

RUN cd /home/drone/catkin_ws/src/uav_mission_planner && pip install -r requirements.txt
# RUN curl https://ctu-mrs.github.io/ppa-stable/add_ppa.sh | bash
# RUN apt-get update && apt-get install -y ros-noetic-mrs-uav-system-full ros-noetic-mrs-uav-gazebo-simulation ros-noetic-mrs-uav-px4-api
# RUN /bin/bash -c "roscd mrs_uav_gazebo_simulation/tmux/one_drone && ./start.sh"
RUN source /home/drone/catkin_ws/install/setup.bash
RUN roslaunch uav_mission_planner launch.launch