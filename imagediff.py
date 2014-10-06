import io
import time
import picamera
import picamera.array
import cv2
import numpy as np

images = list()

with picamera.PiCamera() as camera:
    camera.start_preview()
    camera.resolution = (640, 410)
    camera.iso = 200
    camera.framerate = 30
    time.sleep(2)
#    camera.shutter_speed = camera.exposure_speed
#    camera.exposure_mode = 'off'
#    g = camera.awb_gains
#    camera.awb_mode = 'off'
#    camera.awb_gains = g
    with picamera.array.PiRGBArray(camera) as stream:
	done = False
	for blank in camera.capture_continuous(stream, format='bgr'):
	        stream.truncate()
		stream.seek(0)
		images.append(stream.array)
		if done: 
			break
		done = True
		print("Go!")
		time.sleep(3)
    print("awb" + str(camera.awb_gains))
    print("exposure" + str(camera.shutter_speed))     

#kernel = np.ones((5, 5),np.float32)/25

#for image in images:
#	image = cv2.GaussianBlur(image, (5,5), 0)

diff = cv2.absDiff(images[1], images[0])
#diff = images[1] + images[0]
diff = np.uint8(diff)
images[0] = np.uint8(images[0])
images[1] = np.uint8(images[1])

cv2.imshow("diff", diff)
cv2.imshow("img1", images[0])
cv2.imshow("img2", images[1])
cv2.waitKey()
