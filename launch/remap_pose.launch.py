from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    remap_pose_node = Node(
        package='uav_mission_planner',
        executable='remap_pose_node',
        name='remap_pose_node',
        output='screen'
    )

    return LaunchDescription([
        remap_pose_node,
    ])