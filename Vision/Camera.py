from threading import Thread, Lock
from queue import Queue
import cv2


class Camera:
    """
    Threaded camera class to safely update and read the frames
    Polling is done in a thread to capture the camera stream
    Viewing of the stream has been implemented in a separate thread.

    A frame can be read by using camera.read()
    Camera can be started with camera.start() and viewed with camera.show()
    Camera can be stopped with camera.stop() and the view with camera.end()
    """

    def __init__(self, src=0, width=1280, height=720):
        """
        :param src: defines which camera to use
        :param width: define the width in pixels
        :param height: define the height in pixels
        """
        if src is 0:
            self.stream = cv2.VideoCapture(src)
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        else:
            self.stream = self._cap_stream()

        (self.grabbed, self.frame) = self.stream.read()

        self.frame_width = width
        self.frame_height = height

        self.thread_video_poll = None
        self.thread_video_show = None

        self.polling = False    # Check for the polling thread to see if it's running
        self.viewing = False    # Check for the viewing thread to see if it's running

        self.Q_view = Queue(maxsize=10)     # Polling thread stores frames here for video show thread

        self.read_lock = Lock()

    def start(self):
        """
        Start camera stream capture
        :return: self as object
        """
        if self.polling:
            return None
        self.thread_video_poll = Thread(target=self._update, args=())
        self.polling = True
        self.thread_video_poll.start()
        return self

    def stop(self):
        """
        Stops camera stream capture and view
        """
        self.end()
        if self.polling:
            self.polling = False
            if self.thread_video_poll.is_alive():
                self.thread_video_poll.join(1)

    def _update(self):
        while self.polling:
            if not self.grabbed:
                self.stop()
            else:
                (grabbed, frame) = self.stream.read()
                with self.read_lock:
                    (self.grabbed, self.frame) = grabbed, frame
                if not self.Q_view.full():
                    self.Q_view.put(frame)

    def read(self):
        """
        Reads single frame from the camera stream
        :return: frame
        """
        with self.read_lock:
            frame = self.frame.copy()
        return frame

    def show(self):
        """ View camera stream

        Starts a thread that calls an internal function which uses the cv2.imshow() function.
        cv2.immshow() is not thread safe and there can be only one cv2.imshow() function.
        The cv2.imshow() function should be used on the main thread.

        Be sure to end the view if using cv2.imshow() yourself and start the view when needed again
        by calling Camera.end() and Camera.show() respectively
        """
        if self.viewing:
            return None
        self.thread_video_show = Thread(target=self._view, args=())
        self.viewing = True
        self.thread_video_show.start()

    def end(self):
        """
        Stop viewing camera stream
        """
        if self.viewing:
            self.viewing = False
            cv2.destroyWindow("Video")
            if self.thread_video_show.is_alive():
                self.thread_video_show.join(1)

    def _view(self):
        while self.viewing:
            frame = self.Q_view.get()
            cv2.imshow("Video", frame)
            if cv2.waitKey(1) == 27:
                self.end()
                break

    @staticmethod
    def _cap_stream():
        """
        Connect with a Gstreamer socket that's sending to this terminal
        :return: Captured stream
        """
        # Todo: Check if the stream can be captured or not
        network_video_stream = cv2.VideoCapture(
            'udpsrc port=5000 caps=application/x-rtp,'
            'media=(string)video,'
            'clock-rate=(int)90000,'
            'encoding-name=(string)H264,'
            'payload=(int)96 ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! videoconvert ! appsink ',
            cv2.CAP_GSTREAMER)

        return network_video_stream
