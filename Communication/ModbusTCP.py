import struct
import random

from Communication.SocketConnection import SocketConnection

# All MODBUS/TCP ADU are sent via TCP to registered port 502.
# Remark : the different fields are encoded in Big-endian

# A Modbus frame is composed of an Application Data Unit (ADU), which encloses a Protocol Data Unit (PDU).
# A dedicated header is used on TCP/IP to identify the MODBUS Application Data Unit.
# It is called the MBAP header (MODBUS Application Protocol header)
#
#     ADU = MBAP Header + PDU,
#     PDU = Function code + Data.

# Below the components of the Modbus TCP/IP are listed together with their size in bytes:
# +---------------------------------+
# |   Application Data Unit (ADU)   |
# +---------------+-----------------+
# | **Component** | **Size** (bytes)|
# +---------------+-----------------+
# | MBAP Header   | 7               |
# +---------------+-----------------+
# | PDU           | N               |
# +---------------+-----------------+

# The MBAP header is 7 bytes long and contains the following fields:
# +------------------------+--------------------+--------------------------------------+
# |                    Modbus Application Protocol header (MBAP)                       |
# +------------------------+--------------------+--------------------------------------+
# | **Field**              | **Length** (bytes) | **Description**                      |
# +------------------------+--------------------+--------------------------------------+
# | Transaction identifier | 2                  | Identification of a                  |
# |                        |                    | Modbus request/response transaction. |
# +------------------------+--------------------+--------------------------------------+
# | Protocol identifier    | 2                  | Protocol ID, 0 = Modbus protocol     |
# +------------------------+--------------------+--------------------------------------+
# | Length                 | 2                  | Number of following bytes            |
# +------------------------+--------------------+--------------------------------------+
# | Unit identifier        | 1                  | Identification of a remote slave     |
# |                        |                    | connected on a serial line  or bus   |
# +------------------------+--------------------+--------------------------------------+

# The Protocol Data Unit has a variable length and consists of the following fields:
# +------------------------+--------------------+--------------------------------------+
# |                            Protocol Data Unit (PDU)                                |
# +------------------------+--------------------+--------------------------------------+
# | **Field**              | **Length** (bytes) | **Description**                      |
# +------------------------+--------------------+--------------------------------------+
# | Function code          | 1                  | Function codes as in other variants  |
# +------------------------+--------------------+--------------------------------------+
# | Data                   | n                  | Data as response or commands         |
# +------------------------+--------------------+--------------------------------------+

# Response:
# For a normal response, slave repeats the function code. Should a slave want to report an error,
# it will reply with the requested function code plus 128 (hex 0x80) (3 becomes 131 = hex 0x83),
# and will only include one byte of data, known as the exception code.

# A normal response frame would look like this:
# +----------------------------------+
# |         Response (ADU)           |
# +----------------+-----------------+
# | **Component**  | **Size** (bytes)|
# +----------------+-----------------+
# | MBAP Header    | 7               |
# +----------------+-----------------+
# | Function code  | 1               |
# +----------------+-----------------+
# | Data           | n               |
# +----------------+-----------------+

# An error response frame is 9 bytes long with the following fields
# +----------------------------------+
# |         Response (ADU) (Error)   |
# +----------------+-----------------+
# | **Component**  | **Size** (bytes)|
# +----------------+-----------------+
# | MBAP Header    | 7               |
# +----------------+-----------------+
# | Function code  | 1               |
# +----------------+-----------------+
# | Exception code | 1               |
# +----------------+-----------------+

# For more information on modbus:
# http://www.modbus.org
# http://www.modbus.org/docs/Modbus_Application_Protocol_V1_1b.pdf
# http://www.modbus.org/docs/Modbus_Messaging_Implementation_Guide_V1_0b.pdf


class ModbusTCP:
    """
    A Modbus communication class designed for use with modbusTCP
    """
    __version__ = '0.1'

    # Modbus function code
    READ_COILS = 0x01
    READ_HOLDING_REGISTERS = 0x03

    # Todo: Implement the following modbus functionality:
    # READ_DISCRETE_INPUTS = 0x02
    # READ_INPUT_REGISTERS = 0x04
    # WRITE_SINGLE_COIL = 0x05
    # WRITE_SINGLE_REGISTER = 0x06
    # WRITE_MULTIPLE_COILS = 0x0F
    # WRITE_MULTIPLE_REGISTERS = 0x10

    # Todo: Implement error checking with the following exception codes
    # Modbus exception code
    # ILLEGAL_FUNCTION_CODE = 0x01
    # ILLEGAL_DATA_ACCESS = 0x02  # if the request address is illegal
    # ILLEGAL_DATA_VALUE = 0x03  # if the request data is invalid

    def __init__(self, host, port=502):
        """
        :param host: IP address to connect with
        :param port: Pot (standard 502) to connect with
        """
        self.__transaction_id = 0           # For synchronization between messages of server and client
        self.__protocol_id = 0              # 0 for Modbus/TCP
        self.__unit_id = 0                  # Slave address (255 if not used)

        self.pretty_print_response = False  # Check to print out response message in console

        self.connection = SocketConnection(host, port)

    def open(self):
        """
        Open the socket for communication
        """
        self.connection.connect()

    def close(self):
        """
        Close the socket
        """
        self.connection.disconnect()

    def read_coils(self, bit_address, quantity=1):
        """ Main function 1 of Modbus/TCP - 0x01

        :param bit_address:
        :param quantity:
        :return:
        """
        data_bytes = struct.pack(">HH", bit_address, quantity)
        message = self._create_message(self.READ_COILS, data_bytes)
        return self._send(message)

    def read_holding_registers(self, reg_address, quantity=1):
        """Main function 3 of Modbus/TCP - 0x03.

        Reads the values stored in the registers at the specified addresses.
        :param reg_address: Address of first register to read (16-bit) specified in bytes.
        :param quantity: Number of registers to read (16-bit) specified in bytes
        :return: The values stored in the addresses specified in Bytes
        """
        data_bytes = struct.pack(">HH", reg_address, quantity)
        message = self._create_message(self.READ_HOLDING_REGISTERS, data_bytes)
        return self._send(message)

    def _create_message(self, function_code, data_bytes):
        """
        Create packet in bytes format for sending.
        :param function_code: bytes
        :param data_bytes: bytes
        :return: Bytes modbus packet
        """
        body = struct.pack('>B', function_code) + data_bytes  # create PDU
        self.__transaction_id = random.randint(0, 65535)
        message_length = 1 + len(body)
        header = struct.pack(">HHHB", self.__transaction_id, self.__protocol_id, message_length, self.__unit_id)
        return header + body

    def _send(self, adu):
        """ Send message over the socket

        :param adu: The data to send over the socket
        :return: Bytes response from the other end of the socket
        """
        self.open()
        self.connection.send(adu)
        response = self.connection.receive()
        self.close()

        if self.pretty_print_response:
            self.pretty_print(response)

        if self._error_check(response):
            return None
        return response

    def _error_check(self, response):
        """ Check if the frame is void of errors

        Raises an exception termination the program
        :param response: The ADU to check
        :return: None
        """
        mbap = response[:7]
        function_code = response[7:8]
        mbap = struct.unpack(">HHHB", mbap)

        if mbap[0] != self.__transaction_id:
            print("Modbus: Transaction ID mismatch"
                  "\n - Send: {} \n - Response: {}".format(self.__transaction_id, mbap[0]))
            return True
        elif mbap[1] != self.__protocol_id:
            print("Modbus: Protocol ID mismatch"
                  "\n - Send: {} \n - Response: {}".format(self.__protocol_id, mbap[1]))
            return True
        elif mbap[3] != self.__unit_id:
            print("Modbus: Unit ID mismatch"
                  "\n - Send: {} \n - Response: {}".format(self.__unit_id, mbap[3]))
            return True
        elif mbap[2] != len(response[6:]):
            print("Modbus: Length mismatch"
                  "\n - Length: {} \n - Remaining: {}".format(mbap[2], len(response[6:])))
            return True

        function_code = struct.unpack(">B", function_code)
        if function_code[0] > 127:
            error_code = struct.unpack(">B", response[8:9])
            print("Modbus: Function error: {}".format(error_code))
            return True

        return False

    def set_pretty_print(self, value):
        """
        Enable or disable printing of response message in console
        :param value: Boolean
        """
        self.pretty_print_response = value

    @staticmethod
    def pretty_print(response):
        """ Print Response in the console

        Unpacks the MBAP and function code in readable format
        Data bytes
        :param response:
        """
        mbap = response[:7]
        function_code = response[7:8]
        mbap = struct.unpack(">HHHB", mbap)
        function_code = struct.unpack(">B", function_code)

        print("+--------------------------------------+")
        print("|  ****Modbus TCP Response (ADU)****   |")
        print("+--------------------------------------+")
        print("|    **Header information (MBAP)**     |")
        print("+--------------------------------------+")
        print("| Transaction id: " + str(mbap[0]))
        print("| Protocol id: " + str(mbap[1]))
        print("| Length: " + str(mbap[2]))
        print("| Unit id: " + str(mbap[3]))
        print("+--------------------------------------+")
        print("|     **Data information (PDU)**       |")
        print("+--------------------------------------+")
        print("| Function code: " + str(function_code[0]))
        print("| Data: " + str(response[8:]))
        print("+--------------------------------------+")
        print("\n")
