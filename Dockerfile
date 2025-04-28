FROM ros:foxy

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# Install Gazebo 9 and required packages
RUN apt-get update && \
    apt-get install -y \
    gazebo9 \
    gazebo9-common \
    libgazebo9-dev \
    && apt-get clean

# Install ROS 2 packages
RUN apt-get update && apt-get install -y \
    cmake \
    git \
    libssl-dev \
    libusb-1.0-0-dev \
    pkg-config \
    libgtk-3-dev \
    libglfw3-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \    
    curl \	
    libusb-1.0-0 \
    udev \
    apt-transport-https \
    ca-certificates \
    curl \
    swig \
    software-properties-common \
    python3-pip \
    # ros-foxy-robotis-manipulator \
    && rm -rf /var/lib/apt/lists/*

RUN echo "deb http://packages.ros.org/ros2/ubuntu focal main" > /etc/apt/sources.list.d/ros2-latest.list && \
    curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add -

# Update package list and install MAVROS packages
RUN apt-get update && apt-get install -y \
    ros-foxy-mavros \
    ros-foxy-mavros-extras \
    ros-foxy-mavros-msgs \
    ros-foxy-cv-bridge  \
    geographiclib-tools \
    && rm -rf /var/lib/apt/lists/*

# Install GeographicLib datasets
RUN sudo geographiclib-get-geoids egm96-5 && \
    sudo geographiclib-get-magnetic emm2015


# create a workspace
RUN mkdir -p /root/uav_ws/src/uav_mission_planner
WORKDIR /root/uav_ws
#Clone ZED ROS2 wrapper to src folder
# RUN git clone https://github.com/stereolabs/zed-ros2-wrapper.git /src

# Copy files
COPY . /root/uav_ws/src/uav_mission_planner
# Build the workspace
RUN source /opt/ros/foxy/setup.sh && \
    rosdep install --from-paths src --ignore-src -r -y && \
    colcon build --symlink-install
# Source the workspace
RUN echo "source /root/uav_ws/install/setup.bash" >> ~/.bashrc
# Set the entrypoint
RUN source ~/.bashrc