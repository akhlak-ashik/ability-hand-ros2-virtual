# Full Tutorial: Running the PSYONIC Ability Hand Virtually Without Hardware in ROS 2 Jazzy

This tutorial explains the complete A-to-Z process for running the **PSYONIC Ability Hand** virtually in **RViz** using **ROS 2 Jazzy** on **Ubuntu 24.04**.

The physical Ability Hand hardware is **not required**. Instead, we publish fake joint states to the hand URDF model.

---

## 1. Goal

The goal is to run the Ability Hand virtually so that users can:

- Open the hand model in RViz
- Move the fingers without hardware
- Send custom finger commands
- Create grasp presets
- Test hand visualization before connecting real hardware
- Prepare future integration with robotic arms, MoveIt 2, Gazebo, PyBullet, or Isaac Sim

The core idea is simple:

```text
Fake ROS 2 JointState Publisher  --->  /joint_states_ah  --->  Ability Hand URDF in RViz
```

---

## 2. Tested Environment

```text
Ubuntu: 24.04
ROS 2: Jazzy
Python: 3.12
RViz: RViz 2
Hardware: Not required
```

---

## 3. Install Required Packages

Source ROS 2 Jazzy:

```bash
source /opt/ros/jazzy/setup.bash
```

Install dependencies:

```bash
sudo apt update
sudo apt install -y \
  git \
  python3-pip \
  python3-numpy \
  python3-scipy \
  python3-serial \
  python3-colcon-common-extensions \
  python3-colcon-ros \
  python3-ament-package \
  python3-setuptools \
  ros-jazzy-rclpy \
  ros-jazzy-std-msgs \
  ros-jazzy-sensor-msgs \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-xacro \
  ros-jazzy-rviz2
```

Optional:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 4. Clone the Repository

Create a workspace:

```bash
mkdir -p ~/ability_hand_ws
cd ~/ability_hand_ws
```

Clone your modified repository:

```bash
git clone https://github.com/YOUR_USERNAME/ability-hand-ros2-virtual.git
cd ability-hand-ros2-virtual
```

If you are starting from the original PSYONIC repository:

```bash
git clone -b jazzy https://github.com/psyonicinc/ability-hand-ros2.git
cd ability-hand-ros2
```

---

## 5. Install the Ability Hand Python API

The original repository may suggest installing:

```bash
python3 -m pip install --user ability-hand numpy==1.24 scipy==1.15
```

On Ubuntu 24.04 with Python 3.12, this can fail because the older NumPy version may try to build from source.

Use this instead:

```bash
sudo apt install -y python3-numpy python3-scipy python3-serial
python3 -m pip install --user --break-system-packages --no-deps ability-hand
```

Test:

```bash
python3 -c "import ah_wrapper; print('ah_wrapper imported')"
```

Expected output:

```text
ah_wrapper imported
```

Important:

```text
pip package name: ability-hand
Python import name: ah_wrapper
```

So this is wrong:

```bash
python3 -c "import ability_hand"
```

---

## 6. Build the Workspace

From the repository root:

```bash
cd ~/ability_hand_ws/ability-hand-ros2-virtual
```

Clean previous build files:

```bash
rm -rf build install log
```

Build:

```bash
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

Check packages:

```bash
ros2 pkg list | grep ah
```

Expected packages include:

```text
ah_messages
ah_ros_py
ah_urdf
```

---

## 7. Launch the Ability Hand URDF in RViz

Run:

```bash
ros2 launch urdf_launch display.launch.py
```

This launches the hand model in RViz.

The URDF listens to joint states published on:

```text
/joint_states_ah
```

---

## 8. Why the Original Hardware Launch Fails Without Hardware

The original launch command:

```bash
ros2 launch ah_ros_py hand_wave.launch.py js_publisher:=True
```

starts the real hardware node:

```text
ah_node
```

Without the physical Ability Hand connected, this node fails with:

```text
Could not connect to any hand
```

This is normal.

For virtual use, do not launch the hardware driver. Instead, publish fake joint values to `/joint_states_ah`.

---

## 9. Ability Hand Joint Names

The virtual Ability Hand uses 10 joints:

```text
index_q1
index_q2
middle_q1
middle_q2
ring_q1
ring_q2
pinky_q1
pinky_q2
thumb_q1
thumb_q2
```

The joint order for command input is:

```text
index_q1 index_q2 middle_q1 middle_q2 ring_q1 ring_q2 pinky_q1 pinky_q2 thumb_q1 thumb_q2
```

Finger joints normally move in the positive direction.

The thumb is different:

```text
thumb_q1 = negative direction
thumb_q2 = positive direction
```

Example closed-hand pose:

```text
0.9 0.7 0.9 0.7 0.9 0.7 0.9 0.7 -0.8 0.8
```

---

## 10. Add the Fake Hand-Wave Node

Create:

```bash
nano src/ah_ros_py/ah_ros_py/fake_hand_wave.py
```

Paste:

```python
#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class FakeHandWave(Node):
    def __init__(self):
        super().__init__('fake_hand_wave')

        self.pub = self.create_publisher(JointState, '/joint_states_ah', 10)

        self.joint_names = [
            'index_q1', 'index_q2',
            'middle_q1', 'middle_q2',
            'ring_q1', 'ring_q2',
            'pinky_q1', 'pinky_q2',
            'thumb_q1', 'thumb_q2',
        ]

        self.t = 0.0
        self.timer = self.create_timer(0.02, self.publish_joints)

    def publish_joints(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names

        curl = 0.9 * (0.5 + 0.5 * math.sin(self.t))

        msg.position = [
            curl, curl * 0.75,
            curl, curl * 0.75,
            curl, curl * 0.75,
            curl, curl * 0.75,
            -curl * 0.55, curl * 0.8,
        ]

        self.pub.publish(msg)
        self.t += 0.04


def main(args=None):
    rclpy.init(args=args)
    node = FakeHandWave()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

Make it executable:

```bash
chmod +x src/ah_ros_py/ah_ros_py/fake_hand_wave.py
```

---

## 11. Add the Manual Finger Controller

Create:

```bash
nano src/ah_ros_py/ah_ros_py/manual_finger_control.py
```

Paste:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


JOINT_NAMES = [
    'index_q1', 'index_q2',
    'middle_q1', 'middle_q2',
    'ring_q1', 'ring_q2',
    'pinky_q1', 'pinky_q2',
    'thumb_q1', 'thumb_q2',
]


POSES = {
    "open": [
        0.0, 0.0,
        0.0, 0.0,
        0.0, 0.0,
        0.0, 0.0,
        0.0, 0.0,
    ],
    "close": [
        0.9, 0.7,
        0.9, 0.7,
        0.9, 0.7,
        0.9, 0.7,
        -0.8, 0.8,
    ],
    "pinch": [
        0.8, 0.6,
        0.0, 0.0,
        0.0, 0.0,
        0.0, 0.0,
        -0.9, 0.9,
    ],
    "point": [
        0.0, 0.0,
        0.9, 0.7,
        0.9, 0.7,
        0.9, 0.7,
        -0.7, 0.7,
    ],
    "peace": [
        0.0, 0.0,
        0.0, 0.0,
        0.9, 0.7,
        0.9, 0.7,
        -0.7, 0.7,
    ],
}


class ManualFingerControl(Node):
    def __init__(self):
        super().__init__('manual_finger_control')
        self.pub = self.create_publisher(JointState, '/joint_states_ah', 10)

    def publish_pose(self, positions):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINT_NAMES
        msg.position = positions
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ManualFingerControl()

    print("\nManual PSYONIC Ability Hand Control")
    print("-----------------------------------")
    print("Available commands:")
    print("  open")
    print("  close")
    print("  pinch")
    print("  point")
    print("  peace")
    print()
    print("Custom input order:")
    print("  index_q1 index_q2 middle_q1 middle_q2 ring_q1 ring_q2 pinky_q1 pinky_q2 thumb_q1 thumb_q2")
    print()
    print("Example:")
    print("  0.9 0.7 0.9 0.7 0.9 0.7 0.9 0.7 -0.8 0.8")
    print()
    print("Thumb rule:")
    print("  thumb_q1 = negative")
    print("  thumb_q2 = positive")
    print()
    print("Type q to quit.\n")

    try:
        while rclpy.ok():
            user_input = input("Enter pose or joint values: ").strip().lower()

            if user_input in ["q", "quit", "exit"]:
                break

            if user_input in POSES:
                node.publish_pose(POSES[user_input])
                print(f"Published pose: {user_input}")
                continue

            try:
                values = [float(x) for x in user_input.split()]

                if len(values) != 10:
                    print("Error: Please enter exactly 10 values.")
                    continue

                node.publish_pose(values)
                print("Published custom joint values.")

            except ValueError:
                print("Invalid input. Use a pose name or 10 numeric values.")

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

Make it executable:

```bash
chmod +x src/ah_ros_py/ah_ros_py/manual_finger_control.py
```

---

## 12. Update `setup.py`

Open:

```bash
nano src/ah_ros_py/setup.py
```

Add these lines inside `console_scripts`:

```python
'fake_hand_wave = ah_ros_py.fake_hand_wave:main',
'manual_finger_control = ah_ros_py.manual_finger_control:main',
```

A complete example:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'ah_ros_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your_email@example.com',
    description='ROS 2 virtual control tools for the PSYONIC Ability Hand',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ah_node = ah_ros_py.ah_node:main',
            'hand_wave = ah_ros_py.hand_wave:main',
            'fake_hand_wave = ah_ros_py.fake_hand_wave:main',
            'manual_finger_control = ah_ros_py.manual_finger_control:main',
        ],
    },
)
```

Use your own maintainer name and email.

---

## 13. Optional: Add Launch Files

### Fake hand wave launch

Create:

```bash
mkdir -p src/ah_ros_py/launch
nano src/ah_ros_py/launch/fake_hand_wave.launch.py
```

Paste:

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    urdf_launch_dir = os.path.join(
        get_package_share_directory('urdf_launch'),
        'launch'
    )

    display_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(urdf_launch_dir, 'display.launch.py')
        )
    )

    fake_hand_wave_node = Node(
        package='ah_ros_py',
        executable='fake_hand_wave',
        name='fake_hand_wave',
        output='screen'
    )

    return LaunchDescription([
        fake_hand_wave_node,
        display_launch,
    ])
```

Run with:

```bash
ros2 launch ah_ros_py fake_hand_wave.launch.py
```

### Manual control launch

Create:

```bash
nano src/ah_ros_py/launch/manual_control.launch.py
```

Paste:

```python
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    urdf_launch_dir = os.path.join(
        get_package_share_directory('urdf_launch'),
        'launch'
    )

    display_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(urdf_launch_dir, 'display.launch.py')
        )
    )

    manual_control_node = Node(
        package='ah_ros_py',
        executable='manual_finger_control',
        name='manual_finger_control',
        output='screen',
        emulate_tty=True
    )

    return LaunchDescription([
        display_launch,
        manual_control_node,
    ])
```

Run with:

```bash
ros2 launch ah_ros_py manual_control.launch.py
```

Note: interactive terminal input sometimes works better with:

```bash
ros2 run ah_ros_py manual_finger_control
```

instead of launch.

---

## 14. Rebuild After Code Changes

Every time you add or update Python nodes or launch files, rebuild:

```bash
cd ~/ability_hand_ws/ability-hand-ros2-virtual
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

---

## 15. Run Automatic Virtual Motion

Terminal 1:

```bash
ros2 run ah_ros_py fake_hand_wave
```

Terminal 2:

```bash
ros2 launch urdf_launch display.launch.py
```

Or, if using the launch file:

```bash
ros2 launch ah_ros_py fake_hand_wave.launch.py
```

---

## 16. Run Manual Control

Terminal 1:

```bash
ros2 launch urdf_launch display.launch.py
```

Terminal 2:

```bash
ros2 run ah_ros_py manual_finger_control
```

Then type:

```text
open
close
pinch
point
peace
```

or:

```text
0.9 0.7 0.9 0.7 0.9 0.7 0.9 0.7 -0.8 0.8
```

---

## 17. Publish Directly to the Joint Topic

You can control the virtual hand without any custom Python node.

Open hand:

```bash
ros2 topic pub --once /joint_states_ah sensor_msgs/msg/JointState "
name:
- index_q1
- index_q2
- middle_q1
- middle_q2
- ring_q1
- ring_q2
- pinky_q1
- pinky_q2
- thumb_q1
- thumb_q2
position: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
"
```

Close hand:

```bash
ros2 topic pub --once /joint_states_ah sensor_msgs/msg/JointState "
name:
- index_q1
- index_q2
- middle_q1
- middle_q2
- ring_q1
- ring_q2
- pinky_q1
- pinky_q2
- thumb_q1
- thumb_q2
position: [0.9, 0.7, 0.9, 0.7, 0.9, 0.7, 0.9, 0.7, -0.8, 0.8]
"
```

---

## 18. Check Published Data

```bash
ros2 topic echo /joint_states_ah
```

You should see the joint names and position values being published.

---

## 19. Troubleshooting

### `ModuleNotFoundError: No module named 'ability_hand'`

Use:

```bash
python3 -c "import ah_wrapper"
```

not:

```bash
python3 -c "import ability_hand"
```

---

### `Could not connect to any hand`

This means the real hardware driver was started without hardware connected.

Use the fake nodes instead:

```bash
ros2 run ah_ros_py fake_hand_wave
```

or:

```bash
ros2 run ah_ros_py manual_finger_control
```

---

### Thumb not moving

Use:

```text
thumb_q1 = negative
thumb_q2 = positive
```

Example:

```text
-0.8 0.8
```

---

### Build fails with `--symlink-install`

Use:

```bash
colcon build
```

instead of:

```bash
colcon build --symlink-install
```

---

## 20. Recommended GitHub Repository Structure

```text
ability-hand-ros2-virtual/
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   ├── ah_messages/
│   ├── ah_ros_py/
│   │   ├── ah_ros_py/
│   │   │   ├── ah_node.py
│   │   │   ├── hand_wave.py
│   │   │   ├── fake_hand_wave.py
│   │   │   └── manual_finger_control.py
│   │   ├── launch/
│   │   │   ├── fake_hand_wave.launch.py
│   │   │   └── manual_control.launch.py
│   │   ├── package.xml
│   │   └── setup.py
│   ├── ah_urdf/
│   └── urdf_launch/
├── docs/
│   └── virtual_ability_hand_ros2_jazzy_tutorial.md
└── images/
    └── rviz_demo.png
```

---

## 21. Suggested `.gitignore`

Create:

```bash
nano .gitignore
```

Paste:

```gitignore
build/
install/
log/
__pycache__/
*.pyc
*.pyo
*.egg-info/
.DS_Store
.vscode/
.idea/
*.bag
*.db3
*.sqlite3
```

---

## 22. Publish to GitHub

From the repository root:

```bash
git init
git add .
git commit -m "Add virtual no-hardware Ability Hand control for ROS 2 Jazzy"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ability-hand-ros2-virtual.git
git push -u origin main
```

---

## 23. Conclusion

This virtual setup allows users to test and demonstrate the PSYONIC Ability Hand in ROS 2 Jazzy without the real hardware.

The most important topic is:

```text
/joint_states_ah
```

The virtual controller publishes `sensor_msgs/msg/JointState` messages to this topic, and the Ability Hand URDF updates inside RViz.

This makes the package useful for:

- teaching ROS 2
- prototyping robotic hand control
- designing grasp poses
- preparing demos
- testing before hardware arrives
- integrating the hand with robot arms in future projects
