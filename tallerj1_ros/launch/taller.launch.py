from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

"""Corre todos los nodos del programa"""
def generate_launch_description():
    port_argument = DeclareLaunchArgument(
        "port",
        default_value="auto",
        description="Puerto del ESP32; 'auto' activa la detección automática",
    )

    bridge = Node(
        package="tallerj1_ros",
        executable="serial_bridge",
        name="serial_bridge",
        parameters=[{"port": LaunchConfiguration("port")}],
        output="screen",
    )

    controller = Node(
        package="tallerj1_ros",
        executable="controller",
        name="controller",
        output="screen",
    )

    return LaunchDescription([port_argument, bridge, controller])
