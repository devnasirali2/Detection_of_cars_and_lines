#!/bin/hbpython
#############################################
# Universidad Tecnica Particular de Loja    #
#############################################
# Professor:                                #
# Rodrigo Barba        lrbarba@utpl.edu.ec  #
#############################################
# Students:                                 #
# Marcelo Bravo        mdbravo4@utpl.edu.ec #
# Galo Celly           gscelly@utpl.edu.ec  #
# Nicholas Earley      nearley@utpl.edu.ec  #
#############################################
#Main application: point of entry
# coding=utf-8
__author__ = 'utpl'

# Argument Management Library
import argparse
# Artificial Vision Library
import cv2
# import cv
# Numpy Math Libraries (imported in config, no longer necessary here)
# import numpy as np
# Library for Image Manipulation
from pyimagesearch import imutils
# Library for Frame Timing
import time
# Import Default Values and Constants
from config import *
# Import My Distance Library
import distance as dist
# Import My Mask Library
# import mask as msk
# Import My Video Output Library
# import video as vid
# Import My library for sanitizing data
import sanitize as san

# Manage Arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--car", help="Path to Car Haar Cascade -- default is %s" % car_default)
ap.add_argument("-v", "--video", help="Path to the (optional) video file -- default is Live Webcam Capture")
ap.add_argument("-S", "--scale-factor", help="Haar Cascade Scale Factor -- default is %f" % scaleFactor_default)
ap.add_argument("-N", "--min-neighbors", help="Haar Cascade Minimum Neighbors -- default is %d" % minNeighbors_default)
ap.add_argument("-X", "--roi-x", help="Region Of Interest top left corner X coordinate -- default is %d" % roiX_default)
ap.add_argument("-Y", "--roi-y", help="Region Of Interest top left corner Y coordinate -- default is %d" % roiY_default)
ap.add_argument("-W", "--roi-width", help="Region Of Interest Width -- default is %d" % roiWidth_default)
ap.add_argument("-H", "--roi-height", help="Region Of Interest Height -- default is %d" % roiHeight_default)
ap.add_argument("-x", "--max-line-gap", help="Max Line Gap -- default is %d" % maxLineGap_default)
ap.add_argument("-n", "--min-line-length", help="Min Line Length -- default is %d" % minLineLength_default)
ap.add_argument("-1", "--threshold-1", help="Canny 1st Threshold -- default is %d" % threshold1_default)
ap.add_argument("-2", "--threshold-2", help="Canny 2nd Threshold -- default is %d" % threshold2_default)
ap.add_argument("-a", "--aperture-size", help="Canny Aperture Size -- default is %d" % aperture_size_default)
ap.add_argument("-r", "--rho", help="Hough Rho -- default is %d" % rho_default)
ap.add_argument("-t", "--theta", help="Hough Theta in Radians -- default is %f" % theta_default)
ap.add_argument("-T", "--threshold", help="Hough Threshold -- default is %d" % threshold_default)
ap.add_argument("-D", "--delay", help="Delay for operating system to sleep between frames -- default is %f"
                                      % frameDelay_default)
args = vars(ap.parse_args())
# print args.keys()

# Set defaults for Arguments not provided
car = args['car'] if args['car'] is not None else car_default
scaleFactor = args['scale_factor'] if args['scale_factor'] is not None else scaleFactor_default
minNeighbors = args['min_neighbors'] if args['min_neighbors'] is not None else minNeighbors_default
roiX = args['roi_x'] if args['roi_x'] is not None else roiX_default
roiY = args['roi_y'] if args['roi_y'] is not None else roiY_default
roiWidth = args['roi_width'] if args['roi_width'] is not None else roiWidth_default
roiHeight = args['roi_height'] if args['roi_height'] is not None else roiHeight_default
maxLineGap = args['max_line_gap'] if args['max_line_gap'] is not None else maxLineGap_default
minLineLength = args['min_line_length'] if args['min_line_length'] is not None else minLineLength_default
threshold1 = args['threshold_1'] if args['threshold_1'] is not None else threshold1_default
threshold2 = args['threshold_2'] if args['threshold_2'] is not None else threshold2_default
aperture_size = args['aperture_size'] if args['aperture_size'] is not None else aperture_size_default
rho = args['rho'] if args['rho'] is not None else rho_default
theta = args['theta'] * RADIANS if args['theta'] is not None else theta_default
threshold = args['threshold'] if args['threshold'] is not None else threshold_default
frameDelay = float(args['delay']) if args['delay'] is not None else frameDelay_default

# scaleFactor = scaleFactor_default
# minNeighbors = minNeighbors_default

# Initialize Cascade
car_cascade = cv2.CascadeClassifier(car)

# Initialize Video Stream
if not args.get("video", False):
    camera = cv2.VideoCapture(1)
else:
    camera = cv2.VideoCapture(args["video"])

(grabbed, frame) = camera.read()
if args.get("video") and not grabbed:
    exit(0)

focal_len = focal_len if focal_len is not None else dist.cfg_cam()

print "------------------------------------------------BEGIN------------------------------------------------"

# Video Size Diagnostics
# (grabbed, frame) = camera.read()
# print frame.shape

frame = imutils.resize(frame, width=800)

# Init Video
# vid.vid_init(frame.shape[1], frame.shape[0])

roiY_old = roiY
roiX_old = roiX
roiHeight_old = roiHeight
roiWidth_old = roiWidth

roiX = 0
roiY = frame.shape[0] / 2
roiWidth = frame.shape[1]
roiHeight = frame.shape[0]
print frame.shape

# Frame Selector
frame_num = 0

# (grabbed, frame) = camera.read()
# TODO: Get right shape on mask
# RoadMSK = msk.mkmask(roiWidth, roiHeight, np.array([[(230, 10), (270, 10), (300, 131), (200, 131)]], dtype=np.int32))
# RoadMSK = msk.mkmask(roiWidth, roiHeight, np.array([[(100, 10), (400, 10), (450, 131), (50, 131)]], dtype=np.int32))
# RoadMSK = msk.mkmask(roiWidth, roiHeight, np.array([[(150, 10), (350, 10), (450, 131), (50, 131)]], dtype=np.int32))
# 500 px Width
# RoadMSK = msk.mkmask(roiWidth, roiHeight, np.array([[(110, 10), (390, 10), (490, 131), (10, 131)]], dtype=np.int32))
# 800 px Width
# RoadMSK = msk.mkmask(roiWidth, roiHeight, np.array([[(176, 16), (624, 16), (784, 210), (16, 210)]], dtype=np.int32))
# cv2.imshow("Mask", RoadMSK)

min_def = 100000000
max_def = -100000000
min = min_def
max = max_def
avg = 0.0
cnt = 0
carcnt = 0

avgline = [[[0.0, 0.0], [0.0, 0.0]], [[0.0, 0.0], [0.0, 0.0]], [[0.0, 0.0], [0.0, 0.0]],
           [[0.0, 0.0], [0.0, 0.0]], [[0.0, 0.0], [0.0, 0.0]], [[0.0, 0.0], [0.0, 0.0]],
           [[0.0, 0.0], [0.0, 0.0]], [[0.0, 0.0], [0.0, 0.0]], [[0.0, 0.0], [0.0, 0.0]],
           [[0.0, 0.0], [0.0, 0.0]]]
avgline_count = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

# Main Program Loop
while True:

    # Read Frame
    (grabbed, frame) = camera.read()
    if args.get("video") and not grabbed:
        break

    print "-------------------------BEGIN FRAME %i-------------------------" % frame_num

    # Read only every 5th Frame -- Has no effect on optimization
    '''
    if frame_num % 5 != 0:
        frame_num += 1
        continue
    frame += 1
    # '''

    # Resize Frame
    frame = imutils.resize(frame, width=800)

    # Get size of resized frame
    # print frame.shape

    # Convert Frame to Grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # gray = frame
    # cv2.imshow("Car Detection - Grey", gray)

    # Filter
    #                                 (src, d, sigmaColor, sigmaSpace[, dst[, borderType]])
    grayFiltered = cv2.bilateralFilter(gray, 5, 50, 50)
    grayFiltered = cv2.GaussianBlur(grayFiltered, (5, 5), 3)

    # Apply Histogram
    grayFiltered = cv2.equalizeHist(grayFiltered)
    #                                         (src, ksize, sigmaSpace[, dst[, maxSigmaColor[, anchor[, borderType]]]])
    # grayFiltered = cv2.adaptiveBilateralFilter(gray, 5, 80, 5) # Need Param Example
    # cv2.imshow("Car Detection - Grey Filtered", grayFiltered)

    # Select Area of Interest
    # grayROI = cv.SetImageROI(gray, (roiX, roiY, roiWidth, roiHeight))
    grayROI = grayFiltered[roiY:roiY+roiHeight, roiX:roiX+roiWidth]  # Prior ROI
    # print grayROI.shape
    # preMaskGrayROI = grayFiltered[roiY:roiY+roiHeight, roiX:roiX+roiWidth]
    GrayROI = grayFiltered[roiY:roiY+roiHeight, roiX:roiX+roiWidth]
    # grayROI = msk.applymask(preMaskGrayROI, RoadMSK)
    # print "----------Begin----------"
    # print preMaskGrayROI.shape
    # print RoadMSK.shape
    # print "-----------End-----------"
    # frameROI = frame[roiY:roiY+roiHeight, roiX:roiX+roiWidth]

    # Mask out Unwanted Pixels (Causes Major Slowdown)
    '''
    for irow, row in enumerate(grayROI):
        for icol, pixel in enumerate(row):
            # pixel = 255 if pixel > 150 else 0
            grayROI[irow, icol] = 255 if pixel > 150 else 0
            # print grayROI[irow, icol], ' = ', pixel
    # '''

    # Look for Cars in Area of Interest
    #                                      (image[, scaleFactor[, minNeighbors[, flags[, minSize[, maxSize]]]]])
    carRects = car_cascade.detectMultiScale(grayROI, scaleFactor, minNeighbors)

    # Initialize Canny
    #                 image, edges, threshold1, threshold2, aperture_size=3
    edges = cv2.Canny(grayROI, threshold1, threshold2, apertureSize=aperture_size)
    cv2.imshow("Car Detection - Edges", edges)

    # Detect Lines
    #                      (image, rho, theta, threshold[, lines[, minLineLength[, maxLineGap]]])
    lines2 = cv2.HoughLinesP(edges, rho, theta, threshold, minLineLength, maxLineGap)
    # This Line causes failure (OpenCV side):
    #                     (image, rho, theta, threshold[, lines[, srn[, stn]]])
    # lines = cv2.HoughLines(edges, 1, np.pi/180, 100, minLineLength, maxLineGap)
    lines = cv2.HoughLines(edges, rho, theta, threshold)

    # Make a copy of the current frame
    frameClone = frame.copy()

    # Draw each car rectangle on frame copy
    cri = 1
    for (fX, fY, fW, fH) in carRects:
        cv2.rectangle(frameClone, (fX + roiX, fY + roiY), (fX + fW + roiX, fY + fH + roiY), green, 2)
        d=dist.func_calc_distance(car_width, focal_len, fW)
        cv2.putText(frameClone, "%.1f M" % (d),(fX + fW + roiX + 5, fY + fH/2 + roiY - 5), cv2.FONT_HERSHEY_SIMPLEX,0.9, (0, 255, 0), 3)
        cv2.rectangle(frameClone, (fX + fW/2 + roiX - 5, fY + fH/2 + roiY - 5), (fX + fW/2 + roiX + 5, fY + fH/2 + roiY + 5), (255,255,0), -2)
        print "Distance to object %i is %f" % (cri, d)
        cri += 1

    # Draw each line on frame copy
    if lines is not None:
        for i in range(9, 0, -1):
            avgline[i] = avgline[i-1]
            avgline_count[i] = avgline_count[i-1]
        avgline[0] = [[0.0, 0.0], [0.0, 0.0]]
        avgline_count[0] = [0, 0]
        for line in lines:
            # ''' Display HoughLines
            # ''' New Form with angles
            for r, t in line:
                a = np.cos(t)
                b = np.sin(t)
                ang = np.tan(t + RADIAN_90) / RADIANS
                x0 = a*r
                y0 = b*r
                pt1 = (int(x0 + 1000*(-b) + roiX), int(y0 + 1000*a + roiY))
                pt2 = (int(x0 - 1000*(-b) + roiX), int(y0 - 1000*a + roiY))
                delx = pt1[0] - pt2[0]
                if True:
                    # if -75 <= ang <= -105 or 135 <= ang <= 75:
                    '''
                    if delx == 0:
                        # m = 100000
                        print "HLO (x1, y1) = (%i, %i) (x2, y2) = (%i, %i) m = %f angle = %f"\
                              % (pt1[0], pt2[0], pt1[1], pt2[1], m, ang)
                        #print int(ang)
                        old_ang = ang
                        ang %= 360
                        if old_ang < 0:
                            ang *= -1
                        min = ang if ang < min else min
                        max = ang if ang > max else max
                        avg += ang
                        cnt += 1
                    else:
                    '''
                    if delx != 0:
                        m = (float(pt1[1] - pt2[1]) / float(delx))
                        if m < -0.5 or m > 0.5:
                            # if True:
                            #print "HLO (x1, y1) = (%i, %i) (x2, y2) = (%i, %i) m = %f angle = %f"\
                            #      % (pt1[0], pt2[0], pt1[1], pt2[1], m, ang)
                            # print int(ang)
                            # cv2.line(frameClone, (x1 + roiX, y1 + roiY), (x2 + roiX, y2 + roiY), blue, 1)
                            # Draw all Lines:
                            # cv2.line(frameClone, pt1, pt2, blue, 1)
                            # cv2.line(frameClone, pt1, pt2, white, 1)
                            # Calculate Avg Line:
                            if m < 0:
                                for i in range(10):
                                    avgline[i][1][0] += r
                                    avgline[i][1][1] += t
                                    avgline_count[i][1] += 1
                            elif m > 0:
                                for i in range(10):
                                    avgline[i][0][0] += r
                                    avgline[i][0][1] += t
                                    # print "h"
                                    # print type(avgline_count[i][0])
                                    avgline_count[i][0] += 1
                            old_ang = ang
                            ang %= 360
                            if old_ang < 0:
                                ang *= -1
                            min = ang if ang < min else min
                            max = ang if ang > max else max
                            avg += ang
                            cnt += 1
            # '''
        if avgline_count[9][0] != 0:
            avgline[9][0][0] /= avgline_count[9][0]
            avgline[9][0][1] /= avgline_count[9][0]
        if avgline_count[9][1] != 0:
            avgline[9][1][0] /= avgline_count[9][1]
            avgline[9][1][1] /= avgline_count[9][1]
        tmp_lines = []
        # TODO: Draw Lines up to intersection or roi, which ever has less y
        for avgl in avgline[9]:
            # ''' Display HoughLines
            # ''' New Form with angles
            r = avgl[0]
            t = avgl[1]
            # for r, t in avgl:
            a = np.cos(t)
            b = np.sin(t)
            # print type(t)
            ang = np.tan(t + RADIAN_90) / RADIANS
            x0 = a*r
            y0 = b*r
            pt1 = (int(x0 + 1000*(-b) + roiX), int(y0 + 1000*a + roiY))
            pt2 = (int(x0 - 1000*(-b) + roiX), int(y0 - 1000*a + roiY))
            delx = pt1[0] - pt2[0]
            if delx != 0:
                m = (float(pt1[1] - pt2[1]) / float(delx))
                #print "HLO AVG (x1, y1) = (%i, %i) (x2, y2) = (%i, %i) m = %f angle = %f"\
                #      % (pt1[0], pt1[1], pt2[0], pt2[1], m, ang)
                tmp_lines.append([pt1, pt2, m, ang])
                # print int(ang)
                # Draw all Lines:
                # cv2.line(frameClone, pt1, pt2, blue, 1)
                # cv2.line(frameClone, pt1, pt2, blue, 5)
                # cv2.line(frameClone, pt1, pt2, red, 5)
            else:
                m = 10000
        max_y = roiY
        pti = None
        # print "Need to Crop Lines..."
        # if len(tmp_lines) == 2:
        # TODO: Cut Lines to Point of intersection
        if len(tmp_lines) == 2:
            # data format:
            # tmp_lines[0] = line1
            # tmp_lines[0][0] = line1_pt1
            # tmp_lines[0][0][0] = line1_pt1_x
            # tmp_lines[0][0][1] = line1_pt1_y
            # tmp_lines[0][1] = line1_pt2
            # tmp_lines[0][1][0] = line1_pt2_x
            # tmp_lines[0][1][1] = line1_pt2_y
            # tmp_lines[0][2] = line1_m
            # tmp_lines[0][3] = line1_ang
            # tmp_lines[1] = line2
            # tmp_lines[1][0] = line2_pt1
            # tmp_lines[1][0][0] = line2_pt1_x
            # tmp_lines[1][0][1] = line2_pt1_y
            # tmp_lines[1][1] = line2_pt2
            # tmp_lines[1][1][0] = line2_pt2_x
            # tmp_lines[1][1][1] = line2_pt2_y
            # tmp_lines[1][2] = line2_m
            # tmp_lines[1][3] = line2_ang
            # ----- CALCULATIONS ----- #
            # general form: y = mx + b
            # b = -1 * (mx - y)
            # print "2 Lines: Finding Intersection..."
            b1 = -1 * ((tmp_lines[0][2] * tmp_lines[0][0][0]) - tmp_lines[0][0][1])
            b2 = -1 * ((tmp_lines[1][2] * tmp_lines[1][0][0]) - tmp_lines[1][0][1])
            # line1: y = ax + c
            # line2: y = bx + d
            # ax + c = bx + d
            # a = line1_m = tmp_lines[0][2]
            # b = line2_m = tmp_lines[1][2]
            # c = b1
            # d = b2
            # PoinT of Intersection:
            # pti = ( ((d - c) / (a - b)), ((ad - bc) / (a - b)) )
            pti = (
                ((b2 - b1) / (tmp_lines[0][2] - tmp_lines[1][2])),
                (((tmp_lines[0][2] * b2) - (tmp_lines[1][2] * b1)) / (tmp_lines[0][2] - tmp_lines[1][2]))
            )
            # print "Intersection at: (%d, %d)" % (pti[0], pti[1])
            if pti[1] > max_y:
                max_y = pti[1]
        crop_lines = []
        # if pti is not None and min_y == pti[1]:
        if pti is not None and max_y == pti[1]:
           # print "Cropping Lines to Point of Intersection..."
            for tmpl in tmp_lines:
                if tmpl[0][1] < pti[1]:
                    pt1 = tmpl[1]
                    pt2 = pti
                elif tmpl[1][1] < pti[1]:
                    pt1 = tmpl[0]
                    pt2 = pti
                else:
                    # Should never ever ever enter this condition
                    print "GRAVE ERROR, NON-EXISTENT POINT, POS 394"
                    break
                crop_lines.append([pt1, pt2])
            # print "PTI Cropped Lines: %s" % (str(crop_lines))
        else:
            #print "Cropping Lines to ROI..."
            for tmpl in tmp_lines:
                # x = ((y - y1) / m) + x1
                x1 = tmpl[0][0]
                y1 = tmpl[0][1]
                m = tmpl[2]
                y = roiY
                x = (float(y - y1) / m) + x1
                if tmpl[0][1] < tmpl[1][1]:
                    pt1 = tmpl[1]
                else:
                    pt1 = tmpl[0]
                pt2 = (x, y)
                crop_lines.append([pt1, pt2])
                # print "ROI Cropped Lines: %s" % (str(crop_lines))
        for cropl in crop_lines:
            # pt1 = cropl[0][0]
            # pt2 = cropl[1][0]
            pt1 = cropl[0]
            pt2 = cropl[1]
            print cropl
            print pt1
            print pt2
            # print "pt1 = (%f, %f), pt2 = (%f, %f)" % (pt1[0], pt1[1], pt2[0], pt2[1])
            cv2.line(frameClone, san.double_tuple_2_int(pt1), san.double_tuple_2_int(pt2), blue, 5)
            # print "HLO AVG CROP (x1, y1) = (%i, %i) (x2, y2) = (%i, %i) m = %f angle = %f"\
            #      % (pt1[0], pt1[1], pt2[0], pt2[1], m, ang)
            print "HLO AVG CROP (x1, y1) = (%i, %i) (x2, y2) = (%i, %i) m = %f"\
                  % (pt1[0], pt1[1], pt2[0], pt2[1], ((pt2[1] - pt1[1]) / (pt2[0] - pt1[0])))
    # Second Loop
    if lines2 is not None:
        for line in lines2:
            # ' ''
            # ' '' Display HoughLinesP
            for x1, y1, x2, y2 in line:
                delta_x = float(x1 - x2)
                if delta_x == 0:
                    cv2.line(frameClone, (x1 + roiX, y1 + roiY), (x2 + roiX, y2 + roiY), red, 10)
                else:
                    m = float(y1 - y2) / delta_x
                    # Horizontal lines are between -0.5 and 0.5
                    # if m < -0.75 or m > 0.75:
                    #if m < -0.5 or m > 0.5:
                        # Line is vertical
                       # cv2.line(frameClone, (x1 + roiX, y1 + roiY), (x2 + roiX, y2 + roiY), red, 10)
                        #print "HLP (x1, y1) = (%i, %i) (x2, y2) = (%i, %i) m = %f"\
                        #      % (x1 + roiX, y1 + roiY, x2 + roiX, y2 + roiY, m)
                        # print "Slope is %f" % m
            # '''
        # print lines

    # Show the frame copy
    cv2.imshow("Car Detection - Color", frameClone)

    # Save Video as Images
    # vid.save_frame(frame, frameClone, frame_num)
    # vid.save_vid_frame(frame, frameClone)

    '''
    if cnt >= 29:
        avg /= (cnt + 1)
        print "AVG: %f, CNT: %d, MAX: %f, MIN: %f" % (avg, cnt + 1, max, min)
        cnt = 0
        min = min_def
        max = max_def
        avg = 0.0
    '''

    print "--------------------------END FRAME %i--------------------------" % frame_num
    frame_num += 1

    ''' Pause on Frame Number:
    if frame_num == 1:
        while True:
            if cv2.waitKey(1) & 0xFF == ord("p"):
                break
    # '''

    key = cv2.waitKey(1) & 0xFF

    if key == ord("p"):
        while True:
            if cv2.waitKey(1) & 0xFF == ord("p"):
                break

    # Quit if the User has decided to quit
    if key == ord("q"):
        break

    time.sleep(frameDelay)

avg /= (cnt + 1)
print "AVG: %f, CNT: %d, MAX: %f, MIN: %f" % (avg, cnt + 1, max, min)
print "CARCNT: %d" % carcnt
# vid.close_save()

print "-------------------------------------------------END-------------------------------------------------"
