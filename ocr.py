# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import numpy as np
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
	help="type of preprocessing to be done")
args = vars(ap.parse_args())

# load the example image and convert it to grayscale
image = cv2.imread(args["image"],1)
# image[np.where((image== [0,0,0]).all(axis = 2))] = [255,255,255]
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# check to see if we should apply thresholding to preprocess the
# image
if args["preprocess"] == "thresh":
	gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# make a check to see if median blurring should be done to remove
# noise
elif args["preprocess"] == "blur":
	gray = cv2.medianBlur(gray, 3)

# if args['preprocess'] == 'black':
# 	_,alpha = cv2.threshold(gray,0,255,cv2.THRESH_BINARY)
# 	b, g, r = cv2.split(image)
# 	rgba = [b,g,r,alpha]
# 	gray = cv2.merge(rgba,4)

# write the grayscale image to disk as a temporary file so we can
# apply OCR to it
filename = "{}.png".format(os.getpid())
cv2.imwrite(filename, gray)

# load the image as a PIL/Pillow image, apply OCR, and then delete
# the temporary file
text = pytesseract.image_to_string(Image.open(filename), lang='eng', \
        config='--psm 4 --oem 3 -c tessedit_char_whitelist=0123456789-')
os.remove(filename)
print(text)
 
# show the output images
cv2.imwrite("Image.png", image)
cv2.imwrite("Output.png", gray)

