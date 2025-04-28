from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    line_follower_node = Node(
        package='uav_mission_planner',
        executable='line_follower_node',
        name='node',
        output='screen'
    )

    # Create the launch description
    return LaunchDescription([
        line_follower_node,
    ])