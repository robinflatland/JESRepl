##########################################
# JES Media Functions, Version 13
#
# Adapted from the textbook Introduction
# to Computing and Programming in PYTHON: 
# A multimedia Approach
# by Mark Guzdial and Barbara Ericson
#
# DO NOT MODIFY ANY CODE IN THIS FILE!
#
#
##########################################

from PIL import Image
from scipy.io import wavfile
import sys
import math
import numpy
import PIL
import ImageDraw
import ImageFont
import warnings
from os import walk
from os import listdir
import cv2
import glob

JESColorWrapAround = False #by default
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
yellow = (255,255,0)
cyan = (0,255,255)
magenta = (255,0,255)
orange = (255,165,0)
pink = (255,20,147)
gray = (165,165,165)
darkGray = (120,120,120)
lightGray = (210,210,210)

# Encapsulates the JESPixel data , which includes:
# Data type     Name             Description
# JESImage      self.JESimg      a JESImage object
# integer       self.x           pixel's x (column) location
# integer       self.y           pixel's y (row) location
class JESPixel:
  def __init__(self, JESimg, x, y):
    self.JESimg = JESimg
    self.x = x
    self.y = y

  def __str__(self):
    return "Pixel at (" + str(self.x) + "," + str(self.y) + ") red=" + str(getRed(self)) + " green=" + str(getGreen(self)) + " blue=" + str(getBlue(self))
    
# Encapsulates the JESSample data , which includes:
# Data type     Name             Description
# JESSound      self.JESsnd      a JESSound object
# integer       self.index       sample's index
class JESSample:
  def __init__(self, JESsnd, index ):
    self.JESsnd = JESsnd
    self.index = index

  def __str__(self):
    return "Sample at index " + str(self.index) + " with value " + str( self.JESsnd.samples[ self.index])

# Encapsulates the JESImage data , which includes: 
# Data type     Name             Description
# PIL.Image     self.PILimg      a PIL.Image object
# string        self.filename    name of the image file 
class JESImage:
  # constructor
  def __init__(self, PILimg, filename):
    self.PILimg = PILimg
    self.filename = filename

  # Used when print is called on a JESImage object.
  # Simulates JES behavior (see pg 28 of Guzdial/Ericson text)
  def __str__(self):
    return "Picture, filename " + self.filename + "\n   height " + str(self.PILimg.height) + " width " + str(self.PILimg.width)

# Encapsulates the JESSound data , which includes:
# Data type     Name             Description
# integer       self.sampleRate  the sample rate
# numpy.array   self.samples     1D array of sample values of type numpy.int16
# string        self.filename    name of sound file
class JESSound:
  # constructor
  def __init__(self, sampleRate, samples, filename):
    self.sampleRate = sampleRate
    self.samples = samples
    self.filename = filename
  
  def __str__(self):
    return "Sound, filename " + self.filename + "\n   number of samples " + str(len(self.samples)) + " sample rate " + str(self.sampleRate) 

#########################################################
# JES Image Functions
#########################################################
def makePicture( filename ):
  PILimg = Image.open(filename)
  return JESImage(PILimg, filename)
  

def makeEmptyPicture(width, height, color=(255,255,255)):
  PILimg = PIL.Image.new("RGB", (int(width),int(height)), color)
  return JESImage(PILimg, "noFileName")

def duplicatePicture( JESimg ):
  dup = JESimg.PILimg.copy()
  return JESImage(dup, "noFileName")

def copyInto( smJESimg, lgJESimg, startX, startY):
  lgJESimg.PILimg.paste(smJESimg.PILimg, (int(startX),int(startY)))

def setAllPixelsToAColor(JESimg, color):
  for y in range(0, getHeight(JESimg)):
    for x in range(0, getWidth(JESimg)):
      p = getPixel(JESimg,x,y)
      setColor(p,color)

def getWidth( JESimg ):
  return JESimg.PILimg.width

def getHeight( JESimg ):
  return JESimg.PILimg.height

def getPixel( JESimg, x, y ):
  outOfXRange = ((x < 0) or (x >= getWidth(JESimg)))
  outOfYRange = ((y < 0) or (y >= getHeight(JESimg)))
  if (outOfXRange):
    raise RuntimeError("getPixel(pic, x, y): x was out of range, either it was larger than (getWidth(pic) - 1) or it was less than 0.")
  if (outOfYRange):
    raise RuntimeError("getPixel(pic, x, y): y was out of range, either it was larger than (getHeight(pic) - 1) or it was less than 0.")
  return JESPixel(JESimg, int(x), int(y))

def getPixels( JESimg ):
  allPixels = []
  for x in range(0, getWidth( JESimg )):
    for y in range(0, getHeight( JESimg )):
      allPixels.append( getPixel(JESimg, x, y) )
  return allPixels

def getAllPixels( JESimg ):
  return getPixels( JESimg )

# helper function, not a JES function
def JESWrapAroundValue( value ):
  global JESColorWrapAround
  value = int(value)
  if (JESColorWrapAround == True):
    value = value % 256
  elif value > 255:
    value = 255
  elif value < 0:
    value = 0
  return value

def setRed( JESpix, red ):
  red = JESWrapAroundValue(red)
  color = JESpix.JESimg.PILimg.getpixel((JESpix.x, JESpix.y))
  JESpix.JESimg.PILimg.putpixel((JESpix.x, JESpix.y), (red, color[1], color[2]))

def setBlue( JESpix, blue ):
  blue = JESWrapAroundValue(blue)
  color = JESpix.JESimg.PILimg.getpixel((JESpix.x, JESpix.y))
  JESpix.JESimg.PILimg.putpixel((JESpix.x, JESpix.y), (color[0], color[1], blue))

def setGreen( JESpix, green ):
  green = JESWrapAroundValue(green)
  color = JESpix.JESimg.PILimg.getpixel((JESpix.x, JESpix.y))
  JESpix.JESimg.PILimg.putpixel((JESpix.x, JESpix.y), (color[0], green, color[2]))

def getRed( JESpix ):
  color = JESpix.JESimg.PILimg.getpixel((JESpix.x, JESpix.y))
  return color[0];

def getBlue( JESpix ):
  color = JESpix.JESimg.PILimg.getpixel((JESpix.x, JESpix.y))
  return color[2];

def getGreen( JESpix ):
  color = JESpix.JESimg.PILimg.getpixel((JESpix.x, JESpix.y))
  return color[1];

def getColor( JESpix ):
  return JESpix.JESimg.PILimg.getpixel((JESpix.x, JESpix.y))

def setColor( JESpix, color ):
  r = JESWrapAroundValue(color[0])
  g = JESWrapAroundValue(color[1])
  b = JESWrapAroundValue(color[2])
  JESpix.JESimg.PILimg.putpixel((JESpix.x, JESpix.y), (r, g, b))

def setColorWrapAround( flag ):
  global JESColorWrapAround
  if (flag != True) and (flag != False):
    print("setColorWrapAround( flag ): input flag must be either 1 (True) or 0 (False)  ")
  else:
    JESColorWrapAround = flag

def getColorWrapAround( ):
  global JESColorWrapAround
  return JESColorWrapAround

def makeColor(r,g,b):
  r = JESWrapAroundValue(r)
  g = JESWrapAroundValue(g)
  b = JESWrapAroundValue(b)
  return (r,g,b)

def makeDarker( color ):
  r = int(color[0]*0.80)
  g = int(color[1]*0.80)
  b = int(color[2]*0.80)
  return (r,g,b)

def makeLighter( color ):
  r = min(255,int(color[0]*1.10))
  g = min(255,int(color[1]*1.10))
  b = min(255,int(color[2]*1.10))
  return (r,g,b)

def makeBrighter( color ):
  makeLighter( color )

def getX(JESpix):
  return JESpix.x

def getY(JESpix):
  return JESpix.y

def distance( c1, c2 ):
  dist = (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2
  return math.sqrt(dist)

def writePictureTo( JESimg, filename ):
  # determine if jpg extension on filename
  index = filename.rfind(".")
  if (index == -1): # extension not found
    raise RuntimeError("writePictureTo(pic, filename): filename must have either a .jpg, .jpeg, or .png extension")
  extension = filename[index:len(filename)]
  if ((extension == ".jpg") or (extension == ".jpeg")):
     JESimg.PILimg.save(filename,format="JPEG")
  elif (extension == ".png"):
     JESimg.PILimg.save(filename,format="PNG")
  else:
    raise RuntimeError("writePictureTo(pic, filename): filename must have a .jpg, .jpeg, or .png extension")


def addText(JESimg, xpos, ypos, text, size, color=(0,0,0)):
  # get font
  fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', size)
  # get a drawing context
  d = ImageDraw.Draw(JESimg.PILimg, mode="RGB") 
  # draw text, full opacity
  d.text((int(xpos),int(ypos)), text, font=fnt, fill=color)

def addTextWithStyle(JESimg, xpos, ypos, text, style, color=(0,0,0)):
  # get a drawing context
  d = ImageDraw.Draw(JESimg.PILimg, mode="RGB") 
  # draw text, full opacity
  d.text((int(xpos),int(ypos)), text, font=style, fill=color)

# only allows the size of the font to change
# because I'm not sure what other fonts are available on repl...
def makeStyle( fontName, emphasis, size ):
  return ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', int(size))
  
def addRect(JESimg, startX, startY, width, height, color=(0,0,0)):
  d = ImageDraw.Draw(JESimg.PILimg, mode="RGB")
  d.rectangle([int(startX), int(startY), int(startX+width),int(startY+height)], outline=color,fill=None) 

def addRectFilled(JESimg, startX, startY, width, height, color=(0,0,0)):
  d = ImageDraw.Draw(JESimg.PILimg, mode="RGB")
  d.rectangle([int(startX), int(startY), int(startX+width),int(startY+height)], outline=color,fill=color) 

def addLine(JESimg, startX, startY, endX, endY, color=(0,0,0)):
  d = ImageDraw.Draw(JESimg.PILimg, mode="RGB")
  d.line([int(startX), int(startY), int(endX), int(endY)], fill=color, width=2) 

def addOval(JESimg, startX, startY, width, height, color=(0,0,0)):
  d = ImageDraw.Draw(JESimg.PILimg, mode="RGB")
  d.ellipse([int(startX), int(startY), int(startX+width), int(startY+height)], outline=color, fill=None) 

def addOvalFilled(JESimg, startX, startY, width, height, color=(0,0,0)):
  d = ImageDraw.Draw(JESimg.PILimg, mode="RGB")
  d.ellipse([int(startX), int(startY), int(startX+width), int(startY+height)], outline=color, fill=color) 

def addArc(JESimg, startX, startY, width, height, start, angle, color=(0,0,0)):
  d = ImageDraw.Draw(JESimg.PILimg, mode="RGB")
  d.arc([int(startX), int(startY), int(startX+width), int(startY+height)], int(360-start-angle),int(360-start), fill=color)

def addArcFilled(JESimg, startX, startY, width, height, start, angle, color=(0,0,0)):
  d = ImageDraw.Draw(JESimg.PILimg, mode="RGB")
  d.pieslice([int(startX), int(startY), int(startX+width), int(startY+height)], int(360-start-angle),int(360-start), outline=color,fill=color)  

#########################################################
# JES Sound Functions
#########################################################
def makeSound( filename ):
     warnings.filterwarnings("ignore")
     sampleRate, samples = wavfile.read(filename)
     # Check and see if samples is single channel (mono).
     # It is mono if samples[0] is a number, it is
     # multi-channeled if samples[0] is a numpy.ndarray
     if ( type(samples[0]) is numpy.ndarray):
       # copy data from 1st channel into data (make it mono)
       data = numpy.zeros( len(samples), dtype = numpy.int16 )
       for i in range(0, len(samples)):
         data[i] = samples[i][0] # take just 1st channel
     else:
       data = numpy.copy(samples)
     # samples is read-only array, so make copy that is writeable
     return JESSound(sampleRate, data, filename)
  
def writeSoundTo( JESsnd, filename ):
  #print(JESsnd.samples)
  wavfile.write(filename, JESsnd.sampleRate, JESsnd.samples)

def getLength( JESsnd ):
  return len(JESsnd.samples)

def getNumSamples( JESsnd ):
  return getLength( JESsnd )

def getSampleValueAt( JESsnd, index):
  return JESsnd.samples[index]

def setSampleValueAt( JESsnd, index, val):
  JESsnd.samples[index] = val

def getSamplingRate( JESsnd ):
  return JESsnd.sampleRate

def getSound( JESsam ):
  return JESsam.JESsnd

def getSampleValue( JESsam ):
  return JESsam.JESsnd.samples[ JESsam.index ]
  
def setSampleValue( JESsam, value ):
  JESsam.JESsnd.samples[ JESsam.index ] = value

def getSampleObjectAt(JESsnd, index):
  return JESSample(JESsnd, index)

def getDuration( JESsnd ):
  return getLength(JESsnd)/getSamplingRate(JESsnd)

def getSamples( JESsnd ):
  allSamples = []
  for index in range(0, getLength( JESsnd )):
    allSamples.append( getSampleObjectAt(JESsnd, index ) )
  return allSamples

def duplicateSound( JESsnd ):
  return JESSound( JESsnd.sampleRate, numpy.copy(JESsnd.samples), "noFileName" )

def makeEmptySound( numSamples, sampleRate=22050):
  if ((numSamples <= 0) or (sampleRate <= 0)):
    raise RuntimeError("makeEmptySound(numSamples[, sampleRate]): numSamples and sampleRate must each be greater than 0")
  if (numSamples/sampleRate > 400):
    raise RuntimeError("makeEmptySound(numSamples[, sampleRate]): empty sound length must not exceed 400 seconds")
  samples = numpy.zeros( numSamples, dtype=numpy.int16 )
  return JESSound( sampleRate, samples, "noname")

def makeEmptySoundBySeconds( duration, sampleRate=22050):
  if (sampleRate <= 0):
    raise RuntimeError("makeEmptySoundBySeconds(duration[, sampleRate]): sampleRate must be greater than 0")
  if (duration > 400):
    raise RuntimeError("makeEmptySoundBySeconds(numSamples[, sampleRate]): empty sound length must not exceed 400 seconds")
  samples = numpy.zeros( int(duration*sampleRate), dtype=numpy.int16 )
  return JESSound( sampleRate, samples, "noname")
 
# Animation
#

# returns a list of all files in the folder
def fileList(folder):
  found_files = []
  for (dirpath, dirnames, filenames) in walk(folder):
      found_files.extend(filenames)
      break
  return found_files

def writeMovieTo(images, filename):

  images[0].save(filename,
                  save_all=True, append_images=images[1:], optimize=False, duration=40) #loop=3)


def makeMovieFromInitialFile( firstFile ):
  # Extract path and fileName from firstFile.
  # E.g., if firstFile is animation\frame020.jpg
  # then path will be animation and fileName
  # will be frame020.jpg
  if "//" in firstFile:
    path = firstFile[0:firstFile.rfind("//")]
    fileName = firstFile[firstFile.rfind("//")+2: len(firstFile)]
  else:
    path = ""
    fileName = firstFile

  # get names of all files in the folder and
  # then sort them
  imageFiles = fileList(path)
  imageFiles.sort()
  
  # find fileName in the list of files in the folder
  try : 
    index = imageFiles.index(fileName)
  except ValueError: 
    # fileName not in list
    raise RuntimeError("makeMovieFromInitialFile(firstFile)#: did not find a file with that name")
  
  # remove all names that come before fileName
  imageFiles = imageFiles[index:len(imageFiles)]
  # read in images and put into a list
  images = []
  for f in imageFiles:
    pic = makePicture( path + "//" + f)
    images.append(pic.PILimg)
  
  return images

def writeAnimatedGif( movie, fileName, frameRate=24):
  if frameRate <= 0:
    raise RuntimeError( "writeAnimatedGIF(movie, filename[, frameRate]): frameRate must be greater than zero")
  movie[0].save(fileName,
                save_all=True, append_images=movie[1:], optimize=False, duration=1000/frameRate, loop=0)  

def writeSlideShowTo( fileName, delay=1 ):
  # get names of all files in the folder
  allFiles = []
  for fn in listdir():
    allFiles.append(fn)
  
  # create list containing only
  # files that start with slide   
  # and end with jpg or jpeg
  slideFiles = []
  for fn in allFiles:
    if fn.startswith("slide") and (fn.endswith(".jpg") or fn.endswith(".jpeg")):
      slideFiles.append( fn )
  slideFiles.sort()
  
  # read in images and put into a list
  images = []
  for fn in slideFiles:
    pic = makePicture( fn )
    images.append(pic.PILimg)
  
  # write images as animated gif
  writeAnimatedGif( images, fileName, 1.0/delay )

def makeAVIMovieFromInitialFile( firstFile ):
  # Extract path and fileName from firstFile.
  # E.g., if firstFile is animation\frame020.jpg
  # then path will be animation and fileName
  # will be frame020.jpg
  if "//" in firstFile:
    path = firstFile[0:firstFile.rfind("//")]
    fileName = firstFile[firstFile.rfind("//")+2: len(firstFile)]
  else:
    path = ""
    fileName = firstFile

  # get names of all files in the folder and
  # then sort them
  imageFiles = fileList(path)
  imageFiles.sort()
  
  # find fileName in the list of files in the folder
  try : 
    index = imageFiles.index(fileName)
  except ValueError: 
    # fileName not in list
    raise RuntimeError("makeAVIMovieFromInitialFile(firstFile)#: did not find a file with that name")
    
  
  # remove all names that come before fileName
  imageFiles = imageFiles[index:len(imageFiles)]
  # read in images and put into a list
  img_array = []
  for filename in imageFiles:
    img = cv2.imread(path + "//" + filename)
    img_array.append(img)
  
  return img_array

def writeAVI( movie, fileName, frameRate=24):
  if frameRate <= 0:
    raise RuntimeError( "writeAVI(movie, filename[, frameRate]): frameRate must be greater than zero")
  if (len(movie)) == 0:
    raise RuntimeError("writeAVI(movie,filename[, frameRate]): movie must consist of at least one image")
  height, width, layers = movie[0].shape
  size = (width,height)
  out = cv2.VideoWriter(fileName,cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
  for p in movie:
     out.write(p)
  out.release()

# RETURNS a new sound that is the portion of "source" from "start" to "end"
# doesn't alter the original sound     
def clip (source, start, end):
  target = makeEmptySound (end - start)
  targetIndex = 0
  for sourceIndex in range (start, end):
    sourceValue = getSampleValueAt (source, sourceIndex)
    setSampleValueAt (target, targetIndex, sourceValue)
    targetIndex = targetIndex + 1
  return target
  
# copies the "source" sound into the "target" sound starting at "start" in "target"
def copy (source, target, start):
  targetIndex = start
  for sourceIndex in range(0, getLength(source)):
    sourceValue = getSampleValueAt (source, sourceIndex)
    setSampleValueAt (target, targetIndex, sourceValue)
    targetIndex = targetIndex + 1

# Implementation notes
#
# Implementation of JES image/sound functions
# Version 13 10/6/2020
#   added clip/copy functions for Lab 6
#
# Version 12 8/24/2020 for Img Seq project
#   added writeSlideShowTo function
#
# Version 11, 8/4/2020, Robin Flatland
#
#  8/4/2020
#     writePictureTo allows .jpeg file extension
#  7/30/2020
#     added size input to addText
#     fixed addArcFilled so that it
#     fills the spanned angle.
#  7/23/2020 
#    fixed colorWrapAround to mod by 256
#      rather than 255
#    writePictureTo can write
#      either png or jpg images
#      now, depending on the 
#      file extension. 
#    getPixel now raises a runtime Exception
#       if x or y is out of range
#  7/20/2020
#    took out sys.exit() and sys.quit() &
#      replaced with raising RuntimeException
#      because the exit/quit were resetting the
#      console and forcing the play button to be pressed
#
# Status of implementation of JES functions
# 
# For images, all functions are implemented
# except for:
# makeStyle - only partially implemented.  
#    Currently it only allows the font size 
#    to change. You cannot change the font
#    type or the font formatting (like bold, 
#    italics, etc...) Need to check the default
#    font size also, to see if it is approx.
#    the same as the default in JES.
# pickAColor, pickAFile - WILL NOT BE IMPLEMENTED
# show, repaint - WILL NOT BE IMPLEMENTED
#
# For sounds, all functions are implemented
# except for:
# play, stopPlaying, blockingPlay - WILL NOT BE IMPLEMENTED
# playNote - WILL NOT BE IMPLEMENTED
#
# For animation, we only implemented the functions 
# necessary for the animation project.  Note that
# repl did not allow for easy viewing of AVI movies,
# so for the course we are going with generating
# an animated GIF instead (using the first two 
# functions below). Note that the last three functions
# do not exist in JES by these names:
#    makeMovieFromInitialFile
#    writeAnimatedGif (new function) - one
#       thing is that the animation
#       plays repeatedly.  Did not find a
#       way to make it play only once.
#    makeAVIMovieFromInitialFile (new function)
#    writeAVI (new function)
#
