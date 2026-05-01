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
    "open":  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "close": [0.9, 0.7, 0.9, 0.7, 0.9, 0.7, 0.9, 0.7, -0.8, 0.8],
    "pinch": [0.8, 0.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.9, 0.9],
    "point": [0.0, 0.0, 0.9, 0.7, 0.9, 0.7, 0.9, 0.7, -0.7, 0.7],
    "peace": [0.0, 0.0, 0.0, 0.0, 0.9, 0.7, 0.9, 0.7, -0.7, 0.7],
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

    print("\nManual Ability Hand Control")
    print("Available poses:")
    print("  open")
    print("  close")
    print("  pinch")
    print("  point")
    print("  peace")
    print("\nOr enter 10 joint values:")
    print("Example:")
    print("  0.9 0.7 0.9 0.7 0.9 0.7 0.9 0.7 0.5 0.7")
    print("\nType q to quit.\n")

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
                    print("Please enter exactly 10 values.")
                    continue

                node.publish_pose(values)
                print("Published custom joint values.")

            except ValueError:
                print("Invalid input. Use pose name or 10 numbers.")

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
