# UR-Interface
Interface for communicating with the Universal Robot.\
Contains a Vision module for use with a robot using openCV.

- Python 3.6.7
- OpenCV 3.4.6

Using OpenCV with Gstreamer support enabled

## Robot Interface
**Connect with the robot**

```
host = "192.168.0.1"
robot = URRobot(host)
```


**Set TCP offset**

```
robot.set_tcp((0.05, -0.05, 0.295, 0, 0, 0))
```
First 3 are in metre and the last 3 values are in radians

**Move robot**

```
robot.movel((0.3, -1.0, 0.2, 0, 3.14, 0))
```
First 3 are in metre and the last 3 values are in radians
 
**Get TCP position**

```
robot.get_tcp_position()
```

returns 6 floats as a tuple. First 3 are the vectors in millimeter and last 3 the axis-angle in radians

## Vision Module
The vision module contains the Camera class.\
Camera uses 2 threads to poll and view the stream.\
It uses a lock to read a single frame for procesing.

**Capture stream**

```
src = 0
camera = Camera(src)
camera.start()
```

src 0 will use the first available camera.\
Anything else will try to find a Gstreamer sink streaming to the terminal.

**View Camera stream**

```
camera.show()
```

Note that the this uses the cv2.imshow() function which is not threadsafe.\
Normal use is for the cv2.imshow() function to be used in the main thread.\
The viewing of the camera stream must be ended if using another cv2.imshow().\
If you want to show multiple frames,\
stitch them together and show them via cv2.imshow() in the main thread.

**Stop viewing the camera stream**

```
camera.end()
```

Closes the viewing of the camera stream. The capture stream keeps polling.

**Stop the capture stream**

```
camera.stop()
```

Terminates the viewing of the camera stream and closes the capture stream.

**Read frame**

```
camera.read()
```

Returns the latest frame from the captured stream.
