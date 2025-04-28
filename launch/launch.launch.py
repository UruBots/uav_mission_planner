from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Include the ZED wrapper launch file
    zedm_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('zed_wrapper'),
                'launch',
                'zedm.launch.py'
            ])
        ])
    )

    # Include the MAVROS PX4 launch file
    px4_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('mavros'),
                'launch',
                'px4.launch.py'
            ])
        ])
    )

    # Include the remap pose launch file
    remap_pose_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('uav_mission_planner'),
                'launch',
                'remap_pose_node.launch.py'
            ])
        ])
    )

    return LaunchDescription([
        zedm_launch,
        px4_launch,
        remap_pose_launch,
    ])