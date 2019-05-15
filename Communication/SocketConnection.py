import socket


class SocketConnection:
    """
    Defines a simple interface for connecting to a socket
    """
    def __init__(self, host, port):
        """
        :param host: The IP to connect with
        :param port: Port to connect with
        """
        self.host = host
        self.port = port
        self.opened = False
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """
        Opens a socket connection with the robot for communication.
        :return:
        """
        if self.opened:
            self.disconnect()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(1)

        try:
            self.s.connect((self.host, self.port))
            self.opened = True
        except OSError as error:
            print("Connecting OS error: {0}".format(error))
            return
        return self.s

    def send(self, message):
        """
        Send data over the socket connection
        :param message: The data to send
        :return:
        """
        total_send = 0
        while total_send < len(message):
            send = self.s.send(message[total_send:])
            if send == 0:
                raise RuntimeError("socket connection broken")
            total_send = total_send + send
        self.s.send(message)

    def receive(self):
        """
        Recieve data over the socket connection
        :return:
        """
        response = self.s.recv(1024)
        if len(response) == 0:
            raise RuntimeError("socket connection broken")
        return response

    def disconnect(self):
        """
        Closes the socket connection
        :return:
        """
        try:
            self.s.close()
        except OSError as error:
            print("Disconnecting OS error: {0}".format(error))
            return
