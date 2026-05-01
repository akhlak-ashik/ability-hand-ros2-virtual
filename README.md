# PSYONIC Ability Hand Virtual ROS 2 Jazzy Demo

This repository extends the official **PSYONIC Ability Hand ROS 2** package with virtual no-hardware control examples for **ROS 2 Jazzy** on **Ubuntu 24.04**.

With this package, users can visualize and control the PSYONIC Ability Hand in **RViz** without connecting the physical hand.

## Features

- Run the PSYONIC Ability Hand URDF in RViz
- Simulate finger motion without hardware
- Control fingers manually from terminal input
- Test grasp presets such as open, close, pinch, point, and peace
- Publish custom joint values to `/joint_states_ah`
- Useful for ROS 2 learning, demos, grasp design, and future MoveIt 2 integration

## Tested System

```text
Ubuntu: 24.04
ROS 2: Jazzy
Python: 3.12
Visualization: RViz 2
Hardware: Not required
```

## Original Repository

This project is based on the official PSYONIC Ability Hand ROS 2 repository:

```text
https://github.com/psyonicinc/ability-hand-ros2/tree/jazzy
```

Please keep the original license and credit when redistributing modified code.

---

## Quick Start

### 1. Clone this repository

```bash
mkdir -p ~/ability_hand_ws
cd ~/ability_hand_ws

git clone https://github.com/akhlak-ashik/ability-hand-ros2-virtual.git
cd ability-hand-ros2-virtual
```

---

### 2. Install dependencies

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

Install the PSYONIC Ability Hand Python API:

```bash
python3 -m pip install --user --break-system-packages --no-deps ability-hand
```

Test the Python API:

```bash
python3 -c "import ah_wrapper; print('ah_wrapper imported')"
```

Expected output:

```text
ah_wrapper imported
```

Note: the pip package is named `ability-hand`, but the import name is `ah_wrapper`.

---

### 3. Build the workspace

```bash
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

Optional:

```bash
echo "source ~/ability_hand_ws/ability-hand-ros2-virtual/install/setup.bash" >> ~/.bashrc
```

---

## Run the Virtual Hand

### Option A: Automatic hand wave motion

Terminal 1:

```bash
cd ~/ability_hand_ws/ability-hand-ros2-virtual
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run ah_ros_py fake_hand_wave
```

Terminal 2:

```bash
cd ~/ability_hand_ws/ability-hand-ros2-virtual
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch urdf_launch display.launch.py
```

If you added the included launch file, you can also run:

```bash
ros2 launch ah_ros_py fake_hand_wave.launch.py
```

---

### Option B: Manual finger control

Terminal 1:

```bash
cd ~/ability_hand_ws/ability-hand-ros2-virtual
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch urdf_launch display.launch.py
```

Terminal 2:

```bash
cd ~/ability_hand_ws/ability-hand-ros2-virtual
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run ah_ros_py manual_finger_control
```

Then type one of the following commands:

```text
open
close
pinch
point
peace
```

Or enter custom joint values:

```text
0.9 0.7 0.9 0.7 0.9 0.7 0.9 0.7 -0.8 0.8
```

---

## Joint Names

The virtual Ability Hand uses the following joint order:

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

Important thumb direction:

```text
thumb_q1 = negative direction
thumb_q2 = positive direction
```

A good closed-hand pose is:

```text
0.9 0.7 0.9 0.7 0.9 0.7 0.9 0.7 -0.8 0.8
```

---

## Direct Topic Commands

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

## Troubleshooting

### `ModuleNotFoundError: No module named 'ability_hand'`

This is normal if you are using the wrong import name.

Wrong:

```bash
python3 -c "import ability_hand"
```

Correct:

```bash
python3 -c "import ah_wrapper"
```

---

### `pip install ability-hand numpy==1.24 scipy==1.15` fails

On Ubuntu 24.04, Python 3.12 may fail to build older NumPy versions.

Use:

```bash
sudo apt install -y python3-numpy python3-scipy python3-serial
python3 -m pip install --user --break-system-packages --no-deps ability-hand
```

---

### `Could not connect to any hand`

This happens when the real hardware driver is launched without the physical hand connected.

Avoid this for virtual simulation:

```bash
ros2 launch ah_ros_py hand_wave.launch.py js_publisher:=True
```

Use this instead:

```bash
ros2 run ah_ros_py fake_hand_wave
```

or:

```bash
ros2 run ah_ros_py manual_finger_control
```

---

### Thumb does not move correctly

Use this direction rule:

```text
thumb_q1 = negative
thumb_q2 = positive
```

Example:

```text
-0.8 0.8
```

---

### `colcon build --symlink-install` fails

If you see:

```text
error: option --editable not recognized
```

build without symlink mode:

```bash
colcon build
```

---

## Full Tutorial

See the full step-by-step guide here:

```text
docs/virtual_ability_hand_ros2_jazzy_tutorial.md
```

---

## Acknowledgment

This repository is based on the official PSYONIC Ability Hand ROS 2 repository:

```text
https://github.com/psyonicinc/ability-hand-ros2
```

The original repository is licensed under the MIT License. This modified version adds virtual simulation and manual control examples for ROS 2 Jazzy users who do not have access to the physical hand hardware.
