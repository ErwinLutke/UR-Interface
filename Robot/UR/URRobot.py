from Communication.SocketConnection import SocketConnection
from Robot.UR.URModbusServer import URModbusServer
from Robot.UR.URScript import URScript


class URRobot:
    """
    Interface for communicating with the UR Robot
    SecondaryPort used for sending commands
    ModbusServer used for retrieving info
    """
    def __init__(self, host):
        self.secondaryPort = 30002
        self.secondaryInterface = SocketConnection(host, self.secondaryPort)
        self.secondaryInterface.connect()
        self.URModbusServer = URModbusServer(host)
        self.URScript = URScript()

        # Max safe values of acceleration and velocity are 0.4
        # DO NOT USE THE FOLLOWING VALUES
        # MAX a=1.3962634015954636
        # MAX v=1.0471975511965976
        # These are the absolute max for 'safe' movement and should only be used
        # if you know what your are doing, otherwise you WILL damage the UR internally
        self.acceleration = 0.1
        self.velocity = 0.1

    def movel(self, pose, a=0.1, v=0.1, joint_p=False):
        """Move to position (linear in tool-space)

        See :class:`URScript` for detailed information
        """
        script = URScript.movel(pose, a, v, joint_p=joint_p).encode()
        return self._send_script(script)

    def movej(self, q, a=0.1, v=0.1, joint_p=True):
        """Move to position (linear in joint-space)

        See :class:`URScript` for detailed information
        """
        script = URScript.movej(q, a, v, joint_p=joint_p).encode()
        return self._send_script(script)

    def stopj(self, a=1.5):
        """Stop (linear in joint space)

        See :class:`URScript` for detailed information
        """
        script = URScript.stopj(a).encode()
        return self._send_script(script)

    def set_tcp(self, pose):
        """Set the Tool Center Point

        See :class:`URScript` for detailed information
        """
        script = URScript.set_tcp(pose).encode()
        return self._send_script(script)

    def get_tcp_position(self):
        """ Get TCP position

        Will return values as seen on the teaching pendant (300.0mm)
        :return: 6 Floats - Position data of TCP (x, y, z) in mm (Rx, Ry, Rz) in radials
        """
        position_data = self.URModbusServer.get_tcp_position()
        return position_data

    def set_io(self, io, value):
        """
        Set the specified IO
        :param io: The IO to set as INT
        :param value: Boolean to enable or disable IO
        :return: Boolean to check if the command has been send
        """
        script = "set_digital_out({}, {})".format(io, value) + "\n"
        script = script.encode()
        return self._send_script(script)

    def translate(self, vector, a=0.1, v=0.1):
        """ Move TCP based on its current position

        Example:
        If the TCP position was: 0.4, 0.5, 0.5 and the vector value passed is 0.1, 0.0, 0.0.
        It will attempt to translate the TCP to 0.5, 0.5, 0.5
        :param vector: the X, Y, Z to translate to
        :param a: tool acceleration [m/2^s]
        :param v: tool speed [m/s]
        :return: Boolean to check if the command has been send
        """
        tcp_pos = list(self.get_tcp_position())
        tcp_pos[0] = tcp_pos[0] / 1000 + vector[0]
        tcp_pos[1] = tcp_pos[1] / 1000 + vector[1]
        tcp_pos[2] = tcp_pos[2] / 1000 + vector[2]
        return self.movel(tcp_pos, a, v)

    def _send_script(self, _script):
        """ Send URScript to the UR controller

        :param _script: formatted script to send
        :return: Boolean to check if the script has been send
        """
        try:
            self.secondaryInterface.send(_script)
        except OSError as error:
            print("OS error: {0}".format(error))
            return False
        return True

    @ staticmethod
    def format_cartesian_data(cartesian_data):
        """
        Formats the vector from human readable mm to robot readable mm
        A position of 300mm becomes 0.3
        :param cartesian_data: data to format
        :return: formatted data
        """
        i = 0
        for position in cartesian_data:
            cartesian_data[position] /= (1000 if i < 3 else 1)
            i += 1
        formatted_cartesian_data = cartesian_data

        return formatted_cartesian_data

