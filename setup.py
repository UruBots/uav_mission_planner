import os
from setuptools import find_packages, setup
from glob import glob

package_name = 'uav_mission_planner'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='utec',
    maintainer_email='sbarcelona@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'uav_mission_planner_node = uav_mission_planner.uav_mission_planner_node:main',
            'remap_pose_node = uav_mission_planner.remap_pose_node:main',
            'line_follower_node = uav_mission_planner.line_follower_node:main',
            'qr_code_node = uav_mission_planner.qr_code_node:main',
            'qr_code_detector_node = uav_mission_planner.qr_code_detector_node:main',
            'webcam_publisher_node = uav_mission_planner.webcam_publisher_node:main',
            'object_detector_node = uav_mission_planner.object_detector_node:main',
        ],
    },
)
