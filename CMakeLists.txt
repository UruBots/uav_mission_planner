cmake_minimum_required(VERSION 3.5)
project(uav_mission_planner)

# Buscar dependencias
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(mavros_msgs REQUIRED)

# Instalación de archivos Python
ament_python_install_package(${PROJECT_NAME})

# Instalación de los archivos de lanzamiento
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}/
)

# Instalación de otros recursos
install(
  DIRECTORY resource
  DESTINATION share/${PROJECT_NAME}
)

ament_package()