import picamera
camera = picamera.PiCamera()
camera.capture('image.jpg')
camera.vflip = True
camera.hflip = True
