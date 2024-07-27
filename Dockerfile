FROM ctumrs/mrs_uav_system:latest

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y \
    python3 python3-pip libopencv-dev python3-opencv && \
    rm -rf /var/lib/apt/lists/*  

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
ADD ./fira_challenge_env /home/drone/catkin_ws/src/fira_challenge_env

RUN source /opt/ros/noetic/setup.bash && \
cd /home/drone/catkin_ws && \
catkin_make

RUN cd /home/drone/catkin_ws/src/uav_mission_planner && pip install -r requirements.txt
RUN source /home/drone/catkin_ws/devel/setup.bash && roslaunch mrs_simulation simulation.launch gui:=true world_file:='$(find fira_challenge_env)/worlds/challenge.world'