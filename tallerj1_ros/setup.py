from setuptools import find_packages, setup

package_name = "tallerj1_ros"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/taller.launch.py"]),
    ],
    install_requires=["setuptools"],
    tests_require=["pytest"],
    zip_safe=True,
    maintainer="Vante52",
    maintainer_email="val3kta@gmail.com",
    description="Puente serial y controlador del taller.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "serial_bridge = tallerj1_ros.serial_bridge:main",
            "controller = tallerj1_ros.controller:main",
        ],
    },
)
