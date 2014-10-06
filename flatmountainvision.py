import io
import time
import picamera
import picamera.array
import cv2
import numpy as np
import copy
import RPi.GPIO as GPIO

light_pin = 16
process_threshold = 80
dumping = True
store_prefix = "capture-1-"
iterations = 1
width = 720
height = 480
dpp = float((width*height)/10000)

def start_camera():
    camera = picamera.PiCamera()
    camera.start_preview()
    camera.resolution = (width, height)
    camera.iso = 200
    camera.framerate = 30
    time.sleep(1)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
    return camera

def stop_camera(camera):
    camera.stop_preview()

def capture_images(camera):
    GPIO.output(light_pin, True)
    with picamera.array.PiRGBArray(camera) as stream:
        start_time = time.clock()
        camera.capture(stream, format="bgr", use_video_port=True)
        image1 = stream.array
        stream.truncate()
        stream.seek(0)
        GPIO.output(light_pin, 0)
        camera.capture(stream, format="bgr", use_video_port=True)
        print("Captured two images with " + str(time.clock() - start_time) + " seconds of gap")
        image2 = stream.array
    camera.stop_preview()
    GPIO.output(light_pin, True)
    return image1, image2

def process_images(image1, image2, ):
    start_time = time.clock()
    diff = cv2.absdiff(image1, image2)
    if dumping:
        cv2.imwrite(store_prefix + "diff.jpg", diff)
    greyscale = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    if dumping:
        cv2.imwrite(store_prefix + "greyscale.jpg", greyscale)
    ret, thresholded = cv2.threshold(greyscale, process_threshold, 255, 0)
    if dumping:
        cv2.imwrite(store_prefix + "thresholded.jpg", thresholded)
    contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = list()
    for h, cont in enumerate(contours):
        cont = cv2.convexHull(cont)
        area = float(cv2.contourArea(cont))/dpp
        x, y, w, h = cv2.boundingRect(cont)
        rect_area = float(w*h)/dpp
        if rect_area is 0:
            rect_area = 1
        extent = float(area)/rect_area
        if extent > .5 and area > 50:
           aspect_ratio = float(w)/h
           print("object found: x, y, w, h: {0} {1} {2} {3}, area: {4}, rect_area: {5}, extent: {6}, aspect ratio: {7}".format(x, y, w, h, area, rect_area, extent, aspect_ratio))
           decoration = ""
           if abs(aspect_ratio - 0.2) < .2:
                decoration = "Identified! Vertical Target!"
           if abs(aspect_ratio - 3.5) < 1:
                decoration = "Identified! Horizontal Target!"
           print decoration
           cv2.drawContours(image2, [cont], -1, (255, 0, 0), -1)
           cv2.putText(image2, decoration, (x, y), cv2.FONT_HERSHEY_PLAIN, 2,(0, 255, 255), 2)

    if True:
        cv2.imwrite(store_prefix + "cont.jpg", image2)

    print("Processed images in " + str(time.clock() - start_time) + " seconds")
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(light_pin, GPIO.OUT)
camera = start_camera()
raw_input("Press Enter for camera awesomeness!!!")
for i in range(iterations):
    print("")
    print("")
    print("----Capture " + str(i) + "----")
    print("")
    store_prefix = "capture-" + str(i) + "/"
    image1, image2 = capture_images(camera)
    if dumping:
        cv2.imwrite(store_prefix + "image1.jpg", image1)
        cv2.imwrite(store_prefix + "image2.jpg", image2)
    process_images(image1, image2)
GPIO.cleanup()
