from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    object_detect_node = Node(
        package='uav_mission_planner',
        executable='object_detect_node',
        name='node',
        output='screen'
    )

    return LaunchDescription([
        object_detect_node,
    ])