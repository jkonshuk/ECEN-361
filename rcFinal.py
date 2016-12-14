#Library imports
from SimpleCV import Image
import RPi.GPIO as GPIO
from rrb2 import *
import time
import SimpleCV
import numpy

#Set up the display window 
display = SimpleCV.Display()
cam = SimpleCV.Camera(0, {"width": 480, "height": 240})
normaldisplay = True

#Initialize GPIO pins for motor control
pwmPin = 18
dc = 20 
GPIO.setmode(GPIO.BCM)
GPIO.setup(pwmPin, GPIO.OUT)
pwm = GPIO.PWM(pwmPin, 320)
rr = RRB2()
pwm.start(dc)

#Start the main program loop
while display.isNotDone():

	img   = cam.getImage() #read in the first image
	dist  = img.colorDistance(SimpleCV.Color.BLACK).invert().dilate(1) #Highlight the color black
	dist2 = img.colorDistance(SimpleCV.Color.RED).invert().dilate(1) #Highlight the color red
	segmented  = dist.stretch(210,255) #Set the threshold for what is accepted as black 0-255
	segmented2 = dist2.stretch(150,170) #Same but for red
	blobs  = segmented.findBlobs(minsize=30) #Look for black areas with a minimum size requirement
	blobs2 = segmented2.findBlobs() 

	#this if else block checks the sonar to see if we need to stop or not
	if rr.get_distance() < 30:
		rr.set_motors(0,0,0,0)
		stop = True
	else:
		stop = False

        #compare if it sees the right color and the sonar is clear
	if blobs and not(stop):
                #draw circles around what was found
		img.drawCircle((blobs[-1].x, blobs[-1].y), blobs[-1].radius(), SimpleCV.Color.BLUE,2)
		print(blobs[-1].x,blobs[-1].y)

                #If the object is on the left side of the screen turn right and vice versa
		if blobs[-1].x > 175:
			rr.set_motors(.8,0,.5,1)
		if blobs[-1].x < 155:
			rr.set_motors(.8,0,.5,0)		
	else:
		rr.set_motors(0,0,0,0) #if no track stop

        #If there is something red detected
	if blobs2 and not(stop):
		img.drawCircle((blobs2[-1].x, blobs2[-1].y), blobs2[-1].radius(), SimpleCV.Color.BLUE,2)
		rr.set_motors(0,0,0,0) #stop
		time.sleep(3)          #pause
		rr.set_motors(.8,0,0,0)#resume
		time.sleep(3)

	#display the final processed image
        img.show()
		
#clean up when finished
pwm.stop()
GPIO.cleanup()
