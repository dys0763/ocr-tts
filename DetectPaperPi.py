from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2
import time

camera = PiCamera() #2 functions use camera in different resolution


def get_roi(cnt):
    #identifies each attribute of corners of a given rectangle
    #returns the corners in order of the attribute
    ret = True
    cntindex = [cnt[:, :, 0].argmin(),
                cnt[:, :, 0].argmax(),
                cnt[:, :, 1].argmin(),
                cnt[:, :, 1].argmax()]
                #save the each index of lm(left most), rm(right most), tm(top most), bm(bottom most)
    index = [0, 1, 2, 3]
    indexsort = cntindex.copy()
    indexsort.sort()
    lm = cnt[cntindex[0]][0]
    rm = cnt[cntindex[1]][0]
    if indexsort == index: #case that no index is overlapped
        tm = cnt[cntindex[2]][0]
        bm = cnt[cntindex[3]][0]
        slopeLT = (tm[1] - lm[1]) / (tm[0] - lm[0])
        slopeLB = (bm[1] - lm[1]) / (bm[0] - lm[0])
        if np.isnan(slopeLT) or np.isnan(slopeLB) or np.isinf(slopeLT) or np.isinf(slopeLB): #check error
            ret = False
            print('Wrong Detection! Retrying...')
        elif abs(slopeLT) > abs(slopeLB): #case that a paper is tilted clockwise
            tl = tm
            tr = rm
            bl = lm
            br = bm
        else: #case that a paper is tilted counterclockwise
            tl = lm
            tr = tm
            bl = bm
            br = rm
    else: #case that some index is overlapped
        index.remove(cntindex[0]) #remove index of lm
        index.remove(cntindex[1]) #remove index of rm; so that only 2 indexes remain in variable 'index'
        if cnt[index[0], 0, 1] < min(lm[1], rm[1]) and cnt[index[1], 0, 1] < min(lm[1], rm[1]):
            #case that both remaining cnts is above lm and rm
            bl = lm
            br = rm
            if cnt[index[0],0,0] < cnt[index[1],0,0]:
                tl = cnt[index[0], 0]
                tr = cnt[index[1], 0]
            elif cnt[index[0], 0, 0] > cnt[index[1], 0, 0]:
                tr = cnt[index[0], 0]
                tl = cnt[index[1], 0]
        elif cnt[index[0], 0, 1] > max(lm[1], rm[1]) and cnt[index[1], 0, 1] > max(lm[1], rm[1]):
            #case that both remaining cnts is below lm and rm
            tl = lm
            tr = rm
            if cnt[index[0], 0, 0] < cnt[index[1], 0, 0]:
                bl = cnt[index[0], 0]
                br = cnt[index[1], 0]
            elif cnt[index[0], 0, 0] > cnt[index[1], 0, 0]:
                br = cnt[index[0], 0]
                bl = cnt[index[1], 0]
        else:
            return None, False

    print(tl,tr,bl,br)
    return np.float32([tl, tr, bl, br]), ret #'ret' will be False if destination points can't be determined


def img_projection(img, src_points):
    #transforms perspective
    #returns the trasformed image
    [tl, tr, bl, br] = src_points #sort by clockwise
    w1 = int(((tl[0]-tr[0])**2 + (tl[1]-tr[1])**2)**0.5)
    w2 = int(((bl[0]-br[0])**2 + (bl[1]-br[1])**2)**0.5)
    h1 = int(((tl[0]-bl[0])**2 + (tl[1]-bl[1])**2)**0.5)
    h2 = int(((tr[0]-br[0])**2 + (tr[1]-br[1])**2)**0.5)
    w, h = max(w1, w2), max(h1, h2) #determine width and height
    dst_points = np.float32([[0, 0], [w-1, 0], [0, h-1], [w-1, h-1]])
    projective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    img_out = cv2.warpPerspective(img, projective_matrix, (w, h))
    return img_out


def frame_filter(frame, BIBLUR_SIZE=11, THR_SIZE=31, GAUBLUR_SIZE=(17, 17)):
    #filters an image for detecting a paper
    #returns the filtered image
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_blur = cv2.bilateralFilter(frame_gray, BIBLUR_SIZE, 51, 51)
    frame_thr = cv2.adaptiveThreshold(frame_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, THR_SIZE, 3)
        #use adaptive threshold by large pixel block in order to detect edge of paper well
    frame_edge = ~cv2.Canny(frame_thr, 160, 230)
    frame_blur2 = cv2.GaussianBlur(frame_edge, GAUBLUR_SIZE, 0)
    _, frame_thr2 = cv2.threshold(frame_blur2, 230, 255, 0)
    return frame_thr2


def approx_contour(frame, APPROX_CONSTANT=0.08):
    #finds contours and approximates them in polygon
    #returns the approximated contours
    apx_contour = []
    _, cnts, _ = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in cnts:
        epsilon = APPROX_CONSTANT*cv2.arcLength(cnt, True)
        apx_contour.append(cv2.approxPolyDP(cnt, epsilon, True))
    return apx_contour


def find_paper(RESOLUTION=(320, 480), FRAME_RATE=20, MIN_AREA=0.2, MAX_AREA=0.7, WAIT_TIME=5, END_TIME=60):
    #finds a paper by camera in low resolution
    #returns the coordinates of the paper
    #camera = PiCamera()
    camera.resolution = RESOLUTION
    camera.framerate = FRAME_RATE
    rawCapture = PiRGBArray(camera, size=RESOLUTION)
    print('Camera Launching...')
    start = [time.time(), float(0)]
    print('Detecting will end in {} secs'.format(END_TIME))
    for frm in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        frame = frm.array
        frame_filtered = frame_filter(frame)
        cv2.imshow('frame', frame)
        cnts_apx = approx_contour(frame_filtered)
        area_total = frame.shape[0] * frame.shape[1]
        for cnt in cnts_apx:
            area_cnt = cv2.contourArea(cnt)
            if area_total * MIN_AREA < area_cnt < area_total * MAX_AREA and cv2.isContourConvex(cnt) and len(cnt) == 4:
                #cnt that has appropriate area, is convex and quadrangle is selected
                if start[1] == 0: #when a paper is detected, available detecting will start after a given time
                    start[1] = time.time()
                    print('Wait for {} secs'.format(WAIT_TIME))
                elif time.time() - start[1] > WAIT_TIME:
                    src_points, x = get_roi(cnt)
                    print('Detecting Paper...')
                    if x:
                        print('Paper Detection Succeeded.')
                        return src_points, RESOLUTION, True #have to return the used resolution to find a paper in high resolution
                        break
                cv2.drawContours(frame, [cnt], -1, (0, 0, 255), 3)
                cv2.imshow('frame', frame)
        if time.time() - start[0] > END_TIME: #detecting will end after a given time
            print('Detecting Failed.')
            return None, None, False
            break
        key = cv2.waitKey(1) & 0xff
        rawCapture.truncate(0)
        if key == 27:
            print('Detecting Interrupted.')
            break
    cv2.destroyAllWindows()


def capture_paper(src_points, src_resolution, RESOLUTION=(1280, 1920)):
    #captures the paper in high resolution
    #returns the image of the paper
    camera.resolution = RESOLUTION
    camera.capture('HRimage.jpg')
    img = cv2.imread('HRimage.jpg')
    ratio = [RESOLUTION[i]/src_resolution[i] for i in range(2)]
    ratio_np = np.array([ratio for i in range(4)])
    src_points_float = src_points*ratio_np #multiply the original source points and the ratio of high and low resolution
    src_points_int = np.float32(np.int32(src_points_float))
    img_roi = img_projection(img, src_points_int)
    cv2.imwrite('Paper.jpg', img_roi)
    print('Perspective Projection is Completed.')
    return img_roi
