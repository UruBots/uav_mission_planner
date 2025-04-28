from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # Define nodes to be launched
    # webcam_publisher_node = Node(
    #     package='uav_mission_planner',
    #     executable='webcam_publisher.py',
    #     name='webcam_publisher',
    #     output='screen'
    # )

    # qr_code_detector_node = Node(
    #     package='uav_mission_planner',
    #     executable='qr_code_detector.py',
    #     name='qr_code_detector',
    #     output='screen'
    # )

    # Uncomment the following node if you want to include it
    # qr_to_move_node = Node(
    #     package='uav_mission_planner',
    #     executable='qr_to_move.py',
    #     name='qr_to_move',
    #     output='screen'
    # )

    uav_mission_planner_node = Node(
        package='uav_mission_planner',
        executable='uav_mission_planner_node',
        name='uav_mission_planner',
        output='screen'
    )

    # Create the launch description
    return LaunchDescription([
        # webcam_publisher_node,
        # qr_code_detector_node,
        # qr_to_move_node,  # Uncomment this line if needed
        uav_mission_planner_node,
    ])