#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class FakeHandWave(Node):
    def __init__(self):
        super().__init__('fake_hand_wave')

        # The URDF display is listening to /joint_states_ah
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

        # Finger curl motion in radians
        curl = 0.9 * (0.5 + 0.5 * math.sin(self.t))

        msg.position = [
            curl, curl * 0.75,        # index
            curl, curl * 0.75,        # middle
            curl, curl * 0.75,        # ring
            curl, curl * 0.75,        # pinky
            curl * 0.55, curl * 0.8,  # thumb
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
