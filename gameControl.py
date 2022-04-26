# Copyright @ 2020 ABCOM Information Systems Pvt. Ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================



import numpy as np
import math
import cv2

import pyautogui
from directKeys import up, left, down, right
from directKeys import PressKey, ReleaseKey


def Angle(center_of_frame: list, center: list):
    # print (XYPropio,XYObjetivo)
    if center_of_frame[0] == center[0]:  # angulo 90 o 270
        if center_of_frame[1] > center[1]:
            Angulo = 90
        else:
            Angulo = 270
    elif center_of_frame[1] == center[1]:  # angulo 0 o 180
        if center_of_frame[0] > center[0]:
            Angulo = 180
        else:
            Angulo = 0
    else:  # angulo intermedio
        if center_of_frame[1] > center[1]:
            if center_of_frame[0] < center[0]:
                # print("cuadrante 1","arma")
                Angulo = math.degrees(math.atan(abs(
                    center_of_frame[1] - center[1]) / abs(
                    center_of_frame[0] - center[0])))  # +/-
            else:
                # print("cuadrante 2","arma")
                Angulo = math.degrees(math.atan(-abs(
                    center[1] - center_of_frame[1]) / abs(
                    center[0] - center_of_frame[0]))) + 180
        else:
            if center_of_frame[0] < center[0]:
                # print("cuadrante 4","arma")
                Angulo = math.degrees(math.atan(-abs(
                    center[1] - center_of_frame[1]) / abs(
                    center[0] - center_of_frame[0])))
            else:
                # print("cuadrante 3","arma")
                Angulo = math.degrees(math.atan(abs(
                    center[1] - center_of_frame[1]) / abs(
                    center[0] - center_of_frame[0]))) + 180
    return Angulo



# write the range of lower and upper boundaries of the "blue" object after converting it to hsv region
blueLower = np.array([51,19,90])
blueUpper = np.array([80,250,250])
#declare a variable to capture the real time video of our webcam
video = cv2.VideoCapture(0); 

#set the initial values for parameter to use them later in the code
current_key = set()
#set radius of circle for covering the object
radius_of_circle = 15
#set window size of grabbed frame
window_size = 200
#use Loop until OpenCV window is not closed
while True:
    keyPressed = False
    keyPressed_lr= False
    # to grab the current frame from webcam
    _, grabbed_frame = video.read()
    height,width = grabbed_frame.shape[:2]
    '''GaussianBlur	(	InputArray 	src,
                        OutputArray 	dst,
                        Size 	ksize,
                        double 	sigmaX,
                        double 	sigmaY = 0,
                        int 	borderType = BORDER_DEFAULT)	'''
    #above is the basic syntax of gaussianblur attribute here in our code input array is grabbed_frame, ksize=(11,11) and sigmaY=0
    #the official documentation where you will find the purpose of each element in detail is in below comment
    #https://docs.opencv.org/3.1.0/d4/d86/group__imgproc__filter.html#gaabe8c836e97159a9193fb0b11ac52cf1
    # blur the captured image to make the image smooth and then convert it in hsv color
    #grabbed_frame = imutils.resize(grabbed_frame, width=600)
    
    grabbed_frame = cv2.resize(grabbed_frame, dsize=(600, height))
    blur_frame = cv2.GaussianBlur(grabbed_frame, (11, 11), 0)
    hsv_value = cv2.cvtColor(blur_frame, cv2.COLOR_BGR2HSV)

    # create a cover for object so that you are able to detect the object easily without any
    #  distraction by other details of image you are capturing
    cover = cv2.inRange(hsv_value, blueLower, blueUpper)
    #Erode the masked output
    cover = cv2.erode(cover, None, iterations=2)
    #Dilate the resultant image
    cover = cv2.dilate(cover, None, iterations=2)
    


    # here we will divide the frame into two halves one for up and down keys
    # and other half is for left and right keys by using indexing

    left_cover = cover[:,0:width//2,]
    right_cover = cover[:,width//2:,]

    center_of_frame = [width/2,height/2]

    #define a function to extract the countours from the list 
    def extract_contour(contours):
        if len(contours) == 2:
            contours = contours[0]
            
        elif len(contours) == 3:
            contours = contours[1]

        else:
            raise Exception(("Contours tuple must have length 2 or 3," 
            "otherwise OpenCV changed their cv2.findContours return "
            "signature. Refer to OpenCV's documentation "
            "in that case"))

        return contours
            
    #contours in the left and right frame to find the shape outline of the object for left side
    contour = cv2.findContours(cover.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    #use the defined function to extract from contour_l
    contour = extract_contour(contour)
    centre = None
#RETR_EXTERNAL is for exctracting only outer contour in heirarchy and we use CHAIN_APPROX_SIMPLE here to detect only main point of contour instead of all boundary point
#https://docs.opencv.org/3.4/d9/d8b/tutorial_py_contours_hierarchy.html you can visit this site also for the same

    # start looping if at least one contour or centre is found in left side of frame
    if len(contour) > 0:
        #for creating a circular contour with centroid
        c = max(contour, key=cv2.contourArea)
        ((x, y), r) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        #below is formula for calculating centroid of circle
        centre = (int(M["m10"] / (M["m00"]+0.000001)), int(M["m01"] / (M["m00"]+0.000001)))

        # if the radius meets a minimum size to avoid small distraction of same color then mark it in frame
        if r > radius_of_circle:
            # draw the circle and centroid on the frame,
            cv2.circle(grabbed_frame, (int(x), int(y)), int(r),
                (0, 255, 0), 2)
            cv2.circle(grabbed_frame, centre, 5, (0, 255, 0), -1)

           #set positions where left and right key will be detected

            centre_angle = Angle(center_of_frame,centre)


            #centre_angle >= 45 and centre_angle <= 135
            if 45 < centre_angle < 145:
                cv2.putText(grabbed_frame, 'arriba', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                pyautogui.press('up')
                current_key.add(left)
                keyPressed = True
                keyPressed_lr = True
            elif 145 < centre_angle < 215:
                cv2.putText(grabbed_frame, 'derecha', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                pyautogui.press('right')
                current_key.add(left)
                keyPressed = True
                keyPressed_lr = True
            elif 215 < centre_angle or centre_angle < -40:
                cv2.putText(grabbed_frame, 'abajo', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                pyautogui.press('down')
                current_key.add(left)
                keyPressed = True
                keyPressed_lr = True
            elif -40 < centre_angle < 40:
                cv2.putText(grabbed_frame, 'izquierda', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                pyautogui.press('left')
                current_key.add(left)
                keyPressed = True
                keyPressed_lr = True
            #cv2.putText(grabbed_frame, str(centre_angle), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
            #cv2.putText(grabbed_frame, str(centre), (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)

    # Below code will show the window through which you can see the detection of your object. I named it grabbed_frame
    grabbed_frame_copy = grabbed_frame.copy()
#below line is for creating the blue rectangular box and i set it for user reference because your arrow key will be pressed below and above it
    grabbed_frame_copy = cv2.rectangle(grabbed_frame_copy,(0,height//2 - window_size //2),(width,height//2 + window_size //2),(255,0,0),2)
    cv2.imshow("grabbed_frame", grabbed_frame_copy)


    #release all pressed keys to avoid any glitch


    if not keyPressed and current_key!= 0:
        for key in current_key:

            ReleaseKey(key)
            current_key=set()
 #we use hexadecimal value 0xFF here because when we will press q then it can return other values also if your numlock is activated
    k = cv2.waitKey(1) & 0xFF

    # to stop the loop
    if k == ord("q"):
        break

video.stop()
# close all windows when you will stop capturing video
cv2.destroyAllWindows()
