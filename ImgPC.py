import numpy as np
import cv2
import math


def img_filter(img, SHARP_TIME=2, BLUR_SIZE=7, THR_SIZE=11, THR_COMP=7):
    #filters an image to recognize letters clearly
    #returns the filtered image
    try:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except cv2.error:
        img_gray = img
    kernel_sharpen = np.array([[1, 4, 6, 4, 1], [4, 16, 24, 16, 4],
                               [6, 24, -476, 24, 6], [4, 16, 24, 16, 4], [1, 4, 6, 4, 1]])/256*(-1)
    i = 0
    sharpen = cv2.filter2D(img_gray, -1, kernel_sharpen)
    while i < SHARP_TIME - 1:
        sharpen = cv2.filter2D(sharpen, -1, kernel_sharpen)
        i += 1
    blur = cv2.bilateralFilter(sharpen, BLUR_SIZE, 51, 51)
    thr = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, THR_SIZE, THR_COMP)
    return thr


def letter_contour(img, BLUR_SIZE=(101, 13), THR_VALUE=240):
    #finds contours of boundary of letters
    #returns the contours
    expand1 = cv2.GaussianBlur(img, BLUR_SIZE, 0)
    _, expand2 = cv2.threshold(expand1, THR_VALUE, 255, cv2.THRESH_BINARY)
    _, contours, _ = cv2.findContours(expand2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def contour_degree(contours):
    #finds each slope of contours
    #returns the each degree of slopes
    degree_list = []
    for cnt in contours:
        [vx, vy, _, _] = cv2.fitLine(cnt, cv2.DIST_L12, 0, 0.01, 0.01)
        degree_list.append(math.atan(vy / vx) * 180 / math.pi)
    return degree_list


def degree_select(degree_list, DEGREE_LIMIT=15):
    #sorts degrees out
    #returns the selected degrees
    p_degree = [] #positive degrees
    n_degree = [] #negative degrees
    for valid in degree_list:
        if abs(valid) < DEGREE_LIMIT: #degrees that are over a given limit are discarded
            if valid > 0:
                p_degree.append(valid)
            elif valid < 0:
                n_degree.append(valid)
    if len(p_degree) > len(n_degree): #degrees that are more than another are selected
        return p_degree
    else:
        return n_degree


def exclude_outlier(degree_list, RANGE=0.5):
    #exclues outliers of degrees
    #returns the selected degrees
    mean = np.mean(degree_list)
    std = np.std(degree_list)
    selected_degree = []
    i = 0
    while not selected_degree:
        for degree in degree_list:
            if mean-std*(RANGE+i*0.1) < degree < mean+std*(RANGE+i*0.1):
                selected_degree.append(degree) #degrees that are inside of the standard distribution multiplied by given ratio(RANGE)
        i += 1
    print('Selected Data : within Standard Distribution * {}'.format(RANGE+i*0.1-0.1))
    return selected_degree


def degree_comp(degree, COMP_ORDER=1, COMP_CONSTANT=0.1):
    #complements a degree
    #returns the complemented degree
    compensated_degree = degree + COMP_CONSTANT*degree**COMP_ORDER
    print('Uncompensated Degree = {}'.format(degree))
    print('Compensated Degree = {}'.format(compensated_degree))
    return compensated_degree


def img_rotate(img, degree):
    #rotates an image by a given degree
    #returns the rotated image
    rows, cols = img.shape[:2]
    M0 = cv2.getRotationMatrix2D((cols / 2, rows / 2), degree, 1)
    img_rotate = cv2.warpAffine(img, M0, (cols, rows))
    return img_rotate


def remove_black(img):
    #changes black of corners to white color
    #returns the filtered image
    rows, cols = img.shape[:2]
    mask = np.zeros((rows+2, cols+2), np.uint8)
    corner = [(0, 0), (cols-1, 0), (0, rows-1), (cols-1, rows-1)]
    for i in range(0, 4):
        cv2.floodFill(img, mask, corner[i], 255)
    return img


def main_filter(img):
    #the main image processing
    #returns the totally filtered image
    filtered_img = img_filter(img)
    cnts = letter_contour(filtered_img)
    degrees = contour_degree(cnts)
    degree_sel = degree_select(degrees)
    degree_sel2 = exclude_outlier(degree_sel)
    degree_avg = np.mean(degree_sel2)
    degree_final = degree_comp(degree_avg)
    rotated_img = img_rotate(filtered_img, degree_final)
    final_img = remove_black(rotated_img)
    cv2.imwrite('Filtered Paper Image.jpg', final_img)
    return final_img
