yy
#!/usr/bin/env python
import cv as cv

__author__  = "Blaze Sanders"
__email__   = "blaze.d.a.sanders@gmail.mvp"
__company__ = "Robotic Beverage Technologies, Inc"
__status__  = "Development" 
__date__    = "Late Updated: 2020-05-21"
__doc__     = "Class to control and move LASER system"

# Allow program to create GMT and local timestamps
from time import gmtime, strftime

# Computer Vision module to 
import cv2

import numpy as np

# Robotic Beverage Technologies code for custom data logging and terminal debugging output
from Debug import *

class LASER:

	# Preset LASER power level CONSTANTS (units are Watts)
	HIGH_POWER = 10.00
	STANDARD_POWER = 5.00
	LOW_POWER = 2.50
	DEFAULT_LASER_CONSTANT = 0.05264472  	#TODO Adjust this until LASER branding looks good

	# LASER branding PNG filename CONSTANTS
	RESORT_WORLD_LOGO = "ResortWorldLogoV0.png"
	COCOTAPS_LOGO = "CocoTapsLogoV0.png"
	WYNN_HOTEL_LOGO = "WynnHotelLogoV0.png"
	RED_BULL_LOGO = "RedBullLogoV0.png"
	BACARDI_LOGO = "BacardiLogoV0.png"
	ROYAL_CARRIBBEAN_LOGO = "RoyalCarribbeanLogoV0.png"

	# Global class variable
	laserConstant = -1
	
	def __init__(self, gpioFirePin, supplierPartNumber, cocoPartNumber, powerLevel, maxPowerLevel, brandingArt):
	    """
	    Create a LASER object storing power, part number, and image data to used when fired
	    
	    Key arguments:
        gpioFirePin -- 5V GPIO pin used to control an LASER
	    supplierPartNumber -- External supplier part number (i.e. PA-07-12-5V)
	    cocoPartNumber -- Internal part number (i.e XXX-YYYYY-Z))linked to to one supplier part number
	    powerLevel -- Power in Wats to intialize LASER module to
	    maxPowerLevel -- Max power in Watts that LASER can support in continous operation (> 30 seconds)
	    brandingArt -- Black & White PNG image to brand / burn into an object
	    
	    Return value:
	    Newly created LASER object
	    """	    
	    self.DebugObject = Debug(True)
	    
	    self.gpioFirePin = gpiozero.DigitalOutputDevice(gpioPin)
	    
	    self.powerLevel = powerLevel        # Initialize to 8.0 Watts
	    if(0 > powerLevel or powerLevel > self.maxPowerLevel):
	        # Check for valid power level and default to 10 Watts if invalid
	        Debug.Dprint(DebugOject, "Invalid power. I'm  setting the LASER power to " + repr(self.maxPowerLevel) + " Watts")
	        self.powerLevel = self.maxPowerLevel
	    
	    self.partNumber = partNumber
	    
	    self.brandingArt = COCOTAPS_LOGO	# Initialize to standard CocoTaps logo


	def LoadLImage(fileName):
		"""
		TODO CALL ComputerVision.py code
		
		Load a PNG image on the local harddrive into RAM
		
		Key arguments:
		filename -- PNG file to load into memory
		
		Return value:
		img -- Black & White PNG image
		"""
		print("TODO: CHECK FOR >PNG?")		
		path = "../static/images/" + fileName
		img = cv2.imread(path)
		return img


	def WarpImage(currentImage, coconutSize):
		"""
		Wrap a straight / square image so that after LASER branding on coconut its straight again

		Key arguments:
		currentImage -- Starting PNG image (max size in ? x ? pixels / ?? MB)
		coconutSize -- Horizontal diameter of coconut in millimeters

		Return value:
		newImage -- A new image that has been warpped to to display correctly after LASER branding 
		"""
		# https://docs.opencv.org/2.4/doc/tutorials/core/mat_the_basic_image_container/mat_the_basic_image_container.html
        # https://pythonprogramming.net/loading-images-python-opencv-tutorial/

		#Mat m = Mat() #... // some RGB image
		img = cv.imread(currentImage)
		imgWidth = img.width
		imgHeight = img.height

		for xPixel in range(imgWidth):
			for yPixel in range(imgHeight):
				rgbColor = img.at<Vec3b>(xPixel,yPixel)
				#TODO TRANSLATION
				#Split image into three part vertically and horizonatlly
				##TODO Why we need the below line? Blaze?
				# img.at<Vec3b>(xPixel,yPixel) = rgbColor
				if(xPixel < (imgWidth/5)):
					xPixel = xPixel + 8		# Skip EIGHT pixels since ends warps more at ends
				elif((imgWidth/5) <= xPixel and xPixel < (imgWidth*2/5)):
					xPixel = xPixel + 4		# Skip FOUR pixels since ends warps more at ends
				elif((imgWidth*2/5) <= xPixel and xPixel < (imgWidth*3/5)):
					xPixel = xPixel + 0
				elif((imgWidth*3/5) <= xPixel and xPixel < (imgWidth*4/5)):
					xPixel = xPixel + 4		# Skip FOUR pixels since ends warps more at ends
				elif((imgWidth*4/5) <= xPixel and xPixel < (imgWidth)):
					xPixel = xPixel + 8		# Skip EIGHT pixels since ends wraps more at ends
						

	def ConfigureLaserForNewImage(filename):
		"""
		Calculate firing duration based on LASER power level and image size

        Key arguments:
        filename --

        Return value:
        pixelBurnDuration -- Time in seconds that LASER should dwell on coconut pixel
		"""

		numOfPixels = GetNumOfPixels(filename)
	    moistureLevel = GetCoconutMoistureLevel()

		if(0 < self.powerLevel or self.powerLevel <= LOW_POWER):
			laserConstant = DEFAULT_LASER_CONSTANT * 0.5
		elif(LOW < self.powerLevel or  self.powerLevel < STANDARD_POWER):
			laserConstant = DEFAULT_LASER_CONSTANT * 1.0
		elif(self.powerLevel >= STANDARD_POWER):
			laserConstant = DEFAULT_LASER_CONSTANT * 1.5
		else:
			Debug.Lprint("ERROR: Invalid power level choosen in ConfigureLaserForNewImage() function")

    	pixelBurnDuration = laserConstant * moistureLevel/100.0 * numOfPixels/1000000 

		return pixelBurnDuration


	def StopLaser():
        """
        Toogle GPIO pin connected to high power relay LOW to turn OFF a LASER
        
        Key arguments:
        NONE
        
        Return value:
        NOTHING
        """"
		gpiozero.off(self.gpioFirePin)
		
		
	def BurnImage(filename):
        """
        Toogle GPIO pin connected to high power relay HIGH to turn ON a LASER
        
        Puts CPU to sleep so NOT a threadable function yet
        
        Key arguments:
        filename --
        
        Return value:
        NOTHING
        """"

        pixelDwellDuration = ConfigureLaserForNewImage(filename):
        
        dutyCycle = self.powerLevel/self.maxPowerLevel
        imageBurnComplete = False
        frequency = 100                                         # Desired LASER pulse in Hz
        while(!imageBurnComplete):
            # laserConstant is a class variable
            highTime = 1/frequency  * dutyCycle * laserConstant        
            sleep(highTime)                                     # Sleep upto 10 ms and keep LASER ON
		    gpiozero.on(self.gpioFirePin)
            sleep(0.010 - highTime)                             # Sleep 10 ms minus time is HIGH
		    gpiozero.off(self.gpioFirePin)

            imageBurnComplete = MoveLaserStepperMotor(pixelDwellDuration, frequency)



    def MoveLaserStepperMotor(frequency):
        """
        
        Return value:
        
        """
        for pixelNum in range (0, GetNumOfPixels(filename) - 1):
            
            sleep(pixelDwellDuration + 1/frequency)
            if(pixelNum = )
        

	def SetPowerLevel(watts, cocoPartNumber):
		"""
		Set the power level based on LASER part number being used
		
		Key arguments: 
		watts -- Power in Watts to set LASER output to
		cocoPartNumber -- Internal XXX-YYYYY-Z part number linked to a vendor part number 
		"""
		
		if(cocoPartNumber == "205-00003-A"):
		    if(0 > watts or watts > 10):
                Debug.Dprint(self.DebugObject, "The 400067260113 LASER must have power level between or equal to 0.1 and 10 Watts")
            else:
                self.powerLevel = watts            
		else():
                Debug.Dprint(self.DebugObject, "This LASER supplier part number is not supported in LASER.py code base")
		    
		
	def GetNumOfPixels(filename):
		"""
		Calculate the total number of (pixels / 1,000,000) that is in an image file 
		
		Key argument:
		filename -- PNG file to load into memory
		
		Return value:
		totalNumOfPixels -- Total number of megapixels (million pixels) in an image
		"""
		
		img = LoadLImage(filename)
		#Mat m = ... // some RGB image
		imgWidth = m.width
		imgHeight = m.height
		totalNumOfPixels = imgWidth * imgHeight
		
		return totalNumOfPixels
    
	def GetCoconutMoistureLevel():
		"""
		Moisture level from 0 to 100 corresponing to % humidity
    	
    	Key arguments:
    	NONE
    	
    	Return value:
    	moisturePercentage -- An float from 0.0 to 100.0 
		"""
		
	    #TODO Moisture sensor in fridge
		print("TODO I2C sensor")
		moisturePercentage = 100
		return moisturePercentage
