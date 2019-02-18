import numpy as np
import cv2
import os
import glob
import shutil
import pytesseract
import re
import time

INPUT_DIR = '../Assets/'
OUTPUT_DIR = '../Results/'
REGEX = [r'LVL\s?\d{0,2}', r'[\d,]+\s?[AaPp]{2}', r'Distance[\s]+Walked[\s]+[\d,]+\s?[A-z]{2}']
QUEUE = list()
CROP_AREA = [0, 0, 0, 0]

def apply_threshold(img, argument):
    """ Method to Apply Threshold to the image """

    switcher = {
        1: cv2.threshold(cv2.GaussianBlur(img, (9, 9), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        2: cv2.threshold(cv2.GaussianBlur(img, (7, 7), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        3: cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        4: cv2.threshold(cv2.GaussianBlur(img, (3, 3), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        5: cv2.threshold(cv2.GaussianBlur(img, (1, 1), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        6: cv2.threshold(cv2.medianBlur(img, 9), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        7: cv2.threshold(cv2.medianBlur(img, 7), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        8: cv2.threshold(cv2.medianBlur(img, 5), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        9: cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        10: cv2.threshold(cv2.medianBlur(img, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        11: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (9, 9), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        12: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (7, 7), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        13: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        14: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (3, 3), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        15: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (1, 1), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        16: cv2.adaptiveThreshold(cv2.medianBlur(img, 9), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        17: cv2.adaptiveThreshold(cv2.medianBlur(img, 7), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        18: cv2.adaptiveThreshold(cv2.medianBlur(img, 5), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        19: cv2.adaptiveThreshold(cv2.medianBlur(img, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        20: cv2.adaptiveThreshold(cv2.medianBlur(img, 1), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
    }
    return switcher.get(argument, "Invalid method")

def crop_image(img, start_x, start_y, end_x, end_y):
    """ Method to Crop a Image with x,y coordinates """
    cropped = img[start_y:end_y, start_x:end_x]
    return cropped

def get_string(img_path, method):
    """ Method to get the String from Image after Threshold """

    # Read image using opencv
    img = cv2.imread(img_path)
    file_name = os.path.basename(img_path).split('.')[0]
    file_name = file_name.split()[0]

    output_path = os.path.join(OUTPUT_DIR, file_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Crop the areas where provision number is more likely present
    # img = crop_image(img, CROP_AREA[0], CROP_AREA[1], CROP_AREA[2], CROP_AREA[3])
    # img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    #  Apply threshold to get image with only black and white
    img = apply_threshold(img, method)
    save_path = os.path.join(output_path, file_name + "_filter_" + str(method) + ".jpg")
    cv2.imwrite(save_path, img)

    # Recognize text with tesseract for python
    result = pytesseract.image_to_string(img, lang="eng")

    return result

def find_match(regex, text):
    matches = re.finditer(regex, text, re.MULTILINE)
    target = ""
    for matchNum, match in enumerate(matches):
        matchNum = matchNum + 1

        print("  Match {matchNum} was found at {start}-{end}: {match}".format(matchNum=matchNum, start=match.start(),
                                                                            end=match.end(), match=match.group()))
        target = match.group()

    return target

if __name__ == '__main__':
    
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    im_names = glob.glob(os.path.join(INPUT_DIR, '*.png')) + \
               glob.glob(os.path.join(INPUT_DIR, '*.jpg')) + \
               glob.glob(os.path.join(INPUT_DIR, '*.jpeg'))
    
    overall_start_t = time.time()
    for im_name in sorted(im_names):
        QUEUE.append(im_name)
    print("The following files will be processed and their provision numbers will be extracted: {}\n".format(QUEUE))

    for im_name in im_names:
        start_time = time.time()
        print("*** The documents that are in the queue *** \n{}\n".format(QUEUE))

        print('#=======================================================')
        print(('# Regex is being applied on {:s}'.format(im_name)))
        print('#=======================================================')
        QUEUE.remove(im_name)

        i=1
        while i<=20:
            print("> The filter method " + str(i) + " is now being applied.")
            result = get_string(im_name, i)
            for reg in REGEX:
                match = find_match(reg, result)
                if match:
                    print("MATCH : ",match)
            
            i+=1