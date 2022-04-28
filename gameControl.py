import numpy as np
import math
import cv2
import pyautogui
import sys
from directKeys import up, left, down, right, space
from directKeys import PressKey, ReleaseKey

def extract_contour(contours):
    """
    Extract the countours from the list of detected objects
        Parameters
        ----------
        contours: List
            List of detected objects

        Return
        ------
        contours: List
            List of each detected object's contours
     """
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
    

def angle(center_of_frame: list, center: list):
    """
    Receives the coordinates of a detected object's centre and
    compares it to the coordinates of the camera window's centre
        Parameters
        ----------
        centre_of_frame: List
            Coordinates [x,y] of the window's centre
        centre: List
            Coordinates [x,y] of the object's centre

        Return
        ------
        angle: float
            Relative angle from the window's centre to the
            object's centre
    """      
    if center_of_frame[0] == center[0]:  # angulo 90 o 270
        if center_of_frame[1] > center[1]:
            angle = 90
        else:
            angle = 270
    elif center_of_frame[1] == center[1]:  # angulo 0 o 180
        if center_of_frame[0] > center[0]:
            angle = 180
        else:
            angle = 0
    else:  # angulo intermedio
        if center_of_frame[1] > center[1]:
            if center_of_frame[0] < center[0]:
                # print("cuadrante 1","arma")
                angle = math.degrees(math.atan(abs(
                    center_of_frame[1] - center[1]) / abs(
                    center_of_frame[0] - center[0])))  # +/-
            else:
                # print("cuadrante 2","arma")
                angle = math.degrees(math.atan(-abs(
                    center[1] - center_of_frame[1]) / abs(
                    center[0] - center_of_frame[0]))) + 180
        else:
            if center_of_frame[0] < center[0]:
                # print("cuadrante 4","arma")
                angle = math.degrees(math.atan(-abs(
                    center[1] - center_of_frame[1]) / abs(
                    center[0] - center_of_frame[0])))
            else:
                # print("cuadrante 3","arma")
                angle = math.degrees(math.atan(abs(
                    center[1] - center_of_frame[1]) / abs(
                    center[0] - center_of_frame[0]))) + 180
    return angle



"""
Range of lower and upper boundaries of the "green" and "blue"
objects after converting it to hsv region
"""

greenLower = np.array([51,19,90])
greenUpper = np.array([80,250,250])

blueLower = np.array([90,40,0])
blueUpper = np.array([100,240,255])

"""
Set the initial values of certains parameters to use later
in the code
    Parameters
    ----------
    video: Variable
        A variable to capture the real time video of our webcam
    current_key: Variable
        A variable to capture the key that must be pressed
    radius_of_circle: int
        Sets radius of circle for covering the object
    window_size: int
        Sets window size of grabbed frame
"""
video = cv2.VideoCapture(0);
current_key = set()
radius_of_circle = 15
window_size = 200

"""Loops until OpenCV window is not closed"""
while True:
    keyPressed = False
    # to grab the current frame from webcam
    _, grabbed_frame = video.read()
    height,width = grabbed_frame.shape[:2]
    '''GaussianBlur	(	InputArray 	src,
                        OutputArray 	dst,
                        Size 	ksize,
                        double 	sigmaX,
                        double 	sigmaY = 0,
                        int 	borderType = BORDER_DEFAULT)	'''
    """
    Above is the basic syntax of gaussianblur attribute. Our
    code's input array is grabbed_frame, ksize=(11,11) and
    sigmaY=0

    The official documentation where you will find the purpose
    of each element in detail is in this link
    https://docs.opencv.org/3.1.0/d4/d86/group__imgproc__filter.html#gaabe8c836e97159a9193fb0b11ac52cf1
    """

    """
    Blur the captured image to make the image smooth and then
    convert it in hsv color
    grabbed_frame = imutils.resize(grabbed_frame, width=600)""" 
    grabbed_frame = cv2.resize(grabbed_frame, dsize=(600, height))
    blur_frame = cv2.GaussianBlur(grabbed_frame, (11, 11), 0)
    hsv_value = cv2.cvtColor(blur_frame, cv2.COLOR_BGR2HSV)

    """
    Create a cover for each object so that you are able to
    detect it easily without any distraction by other details
    of the image you are capturing
    """
    cover = cv2.inRange(hsv_value, greenLower, greenUpper)
    cover2 = cv2.inRange(hsv_value, blueLower, blueUpper)
    #Erode the masked output
    cover = cv2.erode(cover, None, iterations=2)
    cover2 = cv2.erode(cover2, None, iterations=2)
    #Dilate the resultant image
    cover = cv2.dilate(cover, None, iterations=2)
    cover2 = cv2.dilate(cover2, None, iterations=2)



    """
    Here we divide the frame into two halves one for up and down keys
    and other half is for left and right keys by using indexing
    ---------
    Not used at the moment, might recycle it later
    """

    left_cover = cover[:,0:width//2,]
    right_cover = cover[:,width//2:,]

    center_of_frame = [width/2,height/2]

            
    """
    Finds contours in the frame to find the shape outline of the
    green object
    """
    green_contour = cv2.findContours(cover.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    green_contour = extract_contour(green_contour)
    centre = None

    """
    Note:
    RETR_EXTERNAL is for exctracting only the outer contour in
    heirarchy and we use CHAIN_APPROX_SIMPLE here to detect only
    the main point of contour instead of all the boundary point
    https://docs.opencv.org/3.4/d9/d8b/tutorial_py_contours_hierarchy.html
    """
    """
    Finds contours in the frame to find the shape outline of the
    blue/cyan object
    """
    blue_contour = cv2.findContours(cover2.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    blue_contour = extract_contour(blue_contour)
    centre2 = None

    """
    Starts looping if at least one blue contour or centre is
    found in the frame"""
    if len(blue_contour) > 0:
        # for creating a circular contour with centroid
        c = max(blue_contour, key=cv2.contourArea)
        ((x, y), r) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        # below is formula for calculating centroid of circle
        centre = (int(M["m10"] / (M["m00"] + 0.000001)), int(M["m01"] / (M["m00"] + 0.000001)))

        # if the radius meets a minimum size to avoid small distraction of same color then mark it in frame
        if r > radius_of_circle:
            # draw the circle and centroid on the frame,
            cv2.circle(grabbed_frame, (int(x), int(y)), int(r),
                       (0, 255, 0), 2)
            cv2.circle(grabbed_frame, centre, 5, (0, 255, 0), -1)
            if not space:
                pyautogui.keyDown("space")
                current_key.add(space)
                keyPressed = True
                space = True
        else:    
            space = False
    print(space)  
    if not space:
        pyautogui.keyUp("space")
                                                                                                                                                                                                                                                       
    """
    Starts looping if at least one green contour or centre is
    found in the frame"""
    if len(green_contour) > 0:
        #for creating a circular contour with centroid
        c = max(green_contour, key=cv2.contourArea)
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

            #Set a relative centre from which a relative angle will be detected
            centre_angle = angle(center_of_frame,centre)

            """
            Relative angle between 45 and 145 -> Object on the 'Up' section
            Relative angle between 145 and 215 -> Object on the 'Right' section
            Relative angle between -40 and 40 -> Object on the 'Left' section
            'Down' section is awkward, so we defined two different threshholds for the relative angle
            """
            if 45 < centre_angle < 145:
                cv2.putText(grabbed_frame, 'arriba', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                pyautogui.press('up')
                current_key.add(up)
                keyPressed = True
            elif 145 < centre_angle < 215:
                cv2.putText(grabbed_frame, 'derecha', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                pyautogui.press('right')
                current_key.add(right)
                keyPressed = True
            elif 215 < centre_angle or centre_angle < -40:
                cv2.putText(grabbed_frame, 'abajo', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                pyautogui.press('down')
                current_key.add(down)
                keyPressed = True
            elif -40 < centre_angle < 40:
                cv2.putText(grabbed_frame, 'izquierda', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                pyautogui.press('left')
                current_key.add(left)
                keyPressed = True
            #cv2.putText(grabbed_frame, str(centre_angle), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
            #cv2.putText(grabbed_frame, str(centre), (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)

    """
    Below code will show the window through which you can see
    the detection of your object
    """
    grabbed_frame_copy = grabbed_frame.copy()
    """
    Below code is for creating the blue rectangular box, we
    should recycle this to draw the direction threshholds
    """
    grabbed_frame_copy = cv2.rectangle(grabbed_frame_copy,(0,height//2 - window_size //2),(width,height//2 + window_size //2),(255,0,0),2)
    cv2.imshow("grabbed_frame", grabbed_frame_copy)

    #Release all pressed keys to avoid any glitch
    if not keyPressed and current_key!= 0:
        for key in current_key:
            if key != "space":
                ReleaseKey(key)
                current_key=set()
    #We use hexadecimal value 0xFF here because when we will press q then it can return other values also if your numlock is activated
    k = cv2.waitKey(1) & 0xFF

    #Press 'q' to stop the loop
    if k == ord("q"):
        break

sys.exit()
