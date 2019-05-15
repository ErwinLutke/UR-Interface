import cv2
import numpy as np
import time

from Robot.UR.URRobot import URRobot
from Vision.Camera import Camera


# Start camera and view it
camera = Camera().start()
camera.show()

host = "192.168.0.11"
robot = URRobot(host)

# Set TCP offset
robot.set_tcp((0.05, -0.05, 0.295, 0, 0, 0))
time.sleep(0.5)

# Set starting position
robot.movel((0.3, -1.0, 0.2, 0, 3.14, 0))


def process_frame(frame):
	"""
	Process the frame and search for circles
	:param frame: frame to process
	:return: processed frame and the found circles
	"""
	# process the snapshot
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	median_blur = cv2.medianBlur(gray, 5, 5)
	# use canny, as HoughCircles seems to prefer ring like circles to filled ones.
	canny = cv2.Canny(median_blur, 100, 150)

	# Finds the circles using Hough Transform
	circles = cv2.HoughCircles(canny, cv2.HOUGH_GRADIENT, 1, 500, param1=85, param2=11, minRadius=50, maxRadius=70)
	circle_data = circles

	if circles is not None:
		# convert the (x, y) coordinates
		circles = np.round(circles[0, :]).astype("int")
		# loop over the (x, y) coordinates and radius of the circles
		c = 0
		for (x, y, r) in circles:
			# draw the circle in the output image
			cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
			cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 0, 255), -1)

			print("Circle " + str(c) + ": " + str(x) + "," + str(y))
			c += 1

	return frame, circle_data


# Todo: Create class around the get_camera_position_data function
# Todo: Create offset input for the camera
def get_camera_position_data(tcp_position, circles):
	"""
	Finds the position data for the TCP based on its current position to center the TCP on the object.
	:param tcp_position: current tcp position (vector and axis)
	:param circles: circle data to process
	:return: Positional data (vector and axis)
	"""
	x_offset = ""
	y_offset = ""

	print("\nCircle Found, Calculating offset...")
	print("Current TCP position:")
	print(tcp_position)

	tcp_position = list(tcp_position)

	circles = np.round(circles[0, :]).astype("int")
	for (_x, _y, _r) in circles:
		print("Circle center on Camera: \n - X: " + str(_x) + " \n - Y: " + str(+ _y))
		x_offset = (1280 / 2) - _x
		y_offset = (720 / 2) - _y

	# Offset calculation
	minus_x = True if x_offset < 0 else False
	minus_y = True if y_offset < 0 else False

	# Calculate the offset based on the units (cm) in 1280 pixel width
	x_offset = (1 / (1280 / 28.5)) * abs(x_offset)
	y_offset = (1 / (1280 / 28.5)) * abs(y_offset)
	print("Offset data: \n - X: " + str(x_offset) + " \n - Y: " + str(y_offset))

	# Set the new offset and center the camera on the object
	tcp_position[0] = tcp_position[0] - y_offset * 10 if minus_y else tcp_position[0] + y_offset * 10
	tcp_position[1] = tcp_position[1] - x_offset * 10 if minus_x else tcp_position[1] + x_offset * 10

	# Align the TCP by using the camera offset towards the TCP
	tcp_position[0] = tcp_position[0] + 47
	tcp_position[1] = tcp_position[1] + 50
	tcp_position[2] = -23

	# Format mm of vectors to one thousandth of mm
	tcp_position[0] /= 1000
	tcp_position[1] /= 1000
	tcp_position[2] /= 1000

	print("New positional data for moving to center of object:")
	print(tcp_position)

	return tcp_position


def bin_picking_2d_coin():
	state = 0
	circles = None

	while True:
		key = cv2.waitKey(1)

		# Processes a camera frame to look for circles
		if key == 102:  # f
			frame = camera.read()  # create snapshot for processing
			frame, circles = process_frame(frame)  # process the frame and search for circles

		elif key == 32:  # space
			# Circle has been found, time to pick it up
			# Take note that we can only work with 1 circle
			# if multiple circles have been found  we will reposition
			if circles is not None and len(circles) == 1:

				# Align the TCP with the object
				tcp_position = robot.get_tcp_position()
				pose = get_camera_position_data(tcp_position, circles)
				robot.movel(pose)
				time.sleep(4)

				# Enable the magnet
				robot.set_io(8, True)
				time.sleep(1)

				# Go to drop-off point
				robot.movel((0.1, -0.75, 0.025, 0, 3.14, 0))

				print("\nWait for drop")
				print("Using modbus to get current position to see if robot is @drop-off point")
				while True:
					pos = robot.get_tcp_position()
					# Check if X and Y are in drop-off range
					if 98 <= abs(pos[0]) <= 102 and 748 <= abs(pos[1]) <= 752:
						break
					else:
						time.sleep(2)
				robot.set_io(8, False)
				print("Dropped\n")

				circles = None
				state = -1

			# No circle has been found so reposition
			else:
				time.sleep(1)
				print("No circle found, repositioning..")
				if state is 0:
					robot.translate((-0.15, 0, 0))
					state = 1
					print("search 0")
				elif state is 1:
					robot.translate((-0.15, 0, 0))
					state = 2
					print("search 1")
				elif state is 2:
					robot.translate((0, -0.15, 0))
					state = 3
					print("search 2")
				elif state is 3:
					robot.translate((0.15, 0, 0))
					state = 4
					print("search 3")
				elif state is 4:
					robot.translate((0.15, 0, 0))
					state = -1
					print("search 4")
				else:
					robot.movel((0.3, -1.0, 0.2, 0.0, 3.14, 0.0))
					print("Returning Home")
					state = 0
		elif key == 27:  # escape
			camera.stop_view()
			camera.stop()
			break

	cv2.destroyAllWindows()
	robot.secondaryInterface.disconnect()

bin_picking_2d_coin()
