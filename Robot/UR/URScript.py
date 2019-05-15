# SW Version 1.8 - URScript manual:
# When connected URScript programs or commands are sent in clear text on the socket.
# Each line is terminated by ’\n’
# python 3 must use bytes (b"") to send the string

# When using URScript the robot moves according to the base plane.

# Joint positions (q) and joint speeds (qd) are represented directly as lists of 6 Floats, one for each robot joint.
# Tool poses (x) are represented as poses also consisting of 6 Floats.
# In a pose, the first 3 coordinates is a position vector and the last 3 an axis-angle


class URScript:
    """ Defines functions for use with the URRobot.

    Based on URScript manual version 1.8
    """
    __version__ = 1.8

    @staticmethod
    def movec(pose_via, pose_to, a=0.1, v=0.1, r=0, joint_p=False):
        """Move Circular: Move to position (circular in tool-space)

        TCP moves on the circular arc segment from current pose, through pose_via to pose_to.
        Accelerates to and moves with constant tool speed v
        :param pose_via: path point (note: only position is used).
        (pose_via can also be specified as joint positions, then forward kinematics is used to
        calculate the corresponding pose)
        :param pose_to: target pose (pose_to can also be specified as joint positions, then
        forward kinematics is used to calculate the corresponding pose
        :param a: tool acceleration [m/2^s]
        :param v: tool speed [m/s]
        :param r: blend radius (of target pose) [m]
        :param joint_p: if True, poses are specified as joint positions
        :return: string containing the movec script
        """
        prefix = "" if joint_p else "p"
        return"movec({}[{}, {}, {}, {}, {}, {}], {}[{}, {}, {}, {}, {}, {}], " \
              "a={}, v={}, r={})".format(prefix, *pose_via, prefix, *pose_to, a, v, r) + "\n"

    @staticmethod
    def movej(q, a=0.1, v=0.1, t=0, r=0, joint_p=True):
        """Move to position (linear in joint-space)

        When using this command, the
        robot must be at standstill or come from a movej or movel with a blend.
        The speed and acceleration parameters controls the trapezoid speed
        profile of the move. The $t$ parameters can be used in stead to set the
        time for this move. Time setting has priority over speed and acceleration
        settings. The blend radius can be set with the $r$ parameters, to avoid
        the robot stopping at the point. However, if he blend region of this mover
        overlaps with previous or following regions, this move will be skipped, and
        an ’Overlapping Blends’ warning message will be generated.
        :param q: joint positions (q can also be specified as a pose, the inverse
        kinematics is used to calculate the corresponding joint positions)
        :param a: joint acceleration of leading axis [rad/sˆ2]
        :param v: joint speed of leading axis [rad/s]
        :param t: time [S]
        :param r: blend radius [m]
        :param joint_p: if True, poses are specified as joint positions
        :return: string containing the movej script
        """
        prefix = "" if joint_p else "p"
        return "movej({}[{}, {}, {}, {}, {}, {}], a={}, v={}, t={}, r={})".format(prefix, *q, a, v, t, r) + "\n"

    @staticmethod
    def movel(pose, a=0.1, v=0.1, t=0, r=0, joint_p=False):
        """Move to position (linear in tool-space)

        :param pose: target pose (pose can also be specified as joint positions,
        then forward kinematics is used to calculate the corresponding pose)
        :param a: tool acceleration [m/2^s]
        :param v: tool speed [m/s]
        :param t: time [S]
        :param r: blend radius [m]
        :param joint_p: if True, poses are specified as joint positions
        :return: string containing the movel script
        """
        prefix = "" if joint_p else "p"
        return "movel({}[{}, {}, {}, {}, {}, {}], a={}, v={}, t={}, r={})".format(prefix, *pose, a, v, t, r) + "\n"

    @staticmethod
    def movep(pose, a=0.1, v=0.1, t=0, r=0, joint_p=False):
        """Move Process

        Blend circular (in tool-space) and move linear (in tool-space) to position.
        Accelerates to and moves with constant tool speed v.
        :param pose: target pose (pose can also be specified as joint positions,
        then forward kinematics is used to calculate the corresponding pose
        :param a: tool acceleration [m/2^s]
        :param v: tool speed [m/s]
        :param t: time [S]
        :param r: blend radius [m]
        :param joint_p: if True, poses are specified as joint positions
        :return: string containing the movep script
        """
        prefix = "" if joint_p else "p"
        return "movep({}[{}, {}, {}, {}, {}, {}], a={}, v={}, t={}, r={})" .format(prefix, *pose, a, v, t, r) + "\n"

    @staticmethod
    def set_tcp(pose):
        """Set the Tool Center Point

        Sets the transformation from the output flange coordinate system to the TCP as a pose.
        :param pose: A pose representing the offset in x, y z and the rotation of the tcp around x, y and z
        :return: A string containing the set tcp script
        """
        return "set_tcp(p[{}, {}, {}, {}, {}, {}])".format(*pose) + "\n"

    @staticmethod
    def stopj(a=1.5):
        """Stop (linear in joint space)

        Decelerate joint speeds to zero
        :param a: joint acceleration [rad/sˆ2] (of leading axis)
        :return: String containing the stopj script
        """
        return "stopj({})".format(a) + "\n"

    @staticmethod
    def stopl(a=0.5):
        """Stop (linear in tool space)

        Decelerate tool speeds to zero
        :param a: joint acceleration [rad/sˆ2] (of leading axis)
        :return: String containing the stopj script
        """
        return "stopl({})".format(a) + "\n"
