from Communication.ModbusTCP import ModbusTCP

import time

# The robot controller acts as a Modbus TCP server (port 502),
# clients can establish connections to it and send standard MODBUS requests to it.

# - Note that some Modbus device manufacturers use the terms Master (client) and Slave (server).
# Typically the external IO device is going to be a server and the robot is going to behave as the client
# (requesting and consuming messages from the server). Master=client and Slave=server.
# However, note that the UR controller can be both a server and a client

# - Note that all values are unsigned, if you want to convert to signed integers,
# program "if (val > 32768): val = val - 65535".
#
# - The MODBUS Server has 0-based addressing.
# Be aware that some other devices are 1-based (e.g. Anybus X-gateways), then just add one to the address
# on that device. (e.g. address 3 on the robot will be address 4 on the Anybus X-gateway)


class URModbusServer:
    """Give read and write access to data in the robot controller for other devices

    An interface for communicating with the modbus TCP server (port 502) on the UR.
    Defines functions for retrieving information from the controller.
    Information will be re-requested if an error occurs.
    All information will be formatted to human readable information.
    """

    def __init__(self, host):
        """
        :param host: IP address to connect with
        """
        self.modbusTCP = ModbusTCP(host, 502)

    def get_tcp_position(self):
        """
        Connects with the Modbus server to requests Cartesian data of the TCP
        :return: Readable cartesian data of TCP, vector in mm, axis in radials
        """
        packet = self.modbusTCP.read_holding_registers(400, quantity=6)

        if packet is None:
            time.sleep(0.5)
            print("Modbus Error: retrying")
            return self.get_tcp_position()
        else:
            x = self._format(packet[9:11]) / 10
            y = self._format(packet[11:13]) / 10
            z = self._format(packet[13:15]) / 10
            rx = self._format(packet[15:17]) / 1000
            ry = self._format(packet[17:19]) / 1000
            rz = self._format(packet[19:21]) / 1000
            return x, y, z, rx, ry, rz

    @staticmethod
    def _format(d):
        """Formats signed integers to unsigned float

        :param d: signed integer to format
        :return: unsigned float
        """
        d = d.hex()
        d_i = int(d, 16)
        d_f = 0

        if d_i < 32768:
            d_f = float(d_i)
        if d_i > 32767:
            d_i = 65535 - d_i
            d_f = float(d_i) * -1
        return d_f
