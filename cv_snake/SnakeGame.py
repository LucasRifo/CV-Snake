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


import random
import pygame
import sys
from pygame.locals import *
from settingsSnakeFun import *
import multiprocessing as mp
import math
import numpy as np
import cv2
from pygame.time import Clock

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


def Camera_Detection(a,b):
    """
    Set the initial values of certains parameters to use later
    in the code
        Parameters
        ----------
        greenLower: np.array
            Lower hsv boundary for green color detection
        greenUpper: np.array
            Upper hsv boundary for green color detection
        blueLower: np.array
            Lower hsv boundary for blue color detection
        blueUpper: np.array
            Upper hsv boundary for blue color detection
        video: Variable
            A variable to capture the real time video of our webcam
        current_key: Variable
            A variable to capture the key that must be pressed
        radius_of_circle: int
            Sets radius of circle for covering the object
        window_size: int
            Sets window size of grabbed frame
        
        center_of_frame
    """
    CLOCK_2 = Clock()

    greenLower = np.array([51, 19, 90])
    greenUpper = np.array([80, 250, 250])

    blueLower = np.array([90, 40, 0])
    blueUpper = np.array([100, 240, 255])
    
    video = cv2.VideoCapture(0);
    current_key = set()
    radius_of_circle = 15
    window_size = 200

    """Loops until OpenCV window is not closed"""

    b.put("READY")

    while True:
        keyPressed = False
        # to grab the current frame from webcam
        _, grabbed_frame = video.read()
        height, width = grabbed_frame.shape[:2]
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
        # Erode the masked output
        cover = cv2.erode(cover, None, iterations=2)
        cover2 = cv2.erode(cover2, None, iterations=2)
        # Dilate the resultant image
        cover = cv2.dilate(cover, None, iterations=2)
        cover2 = cv2.dilate(cover2, None, iterations=2)

        center_of_frame = [width / 2, height / 2]

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

        """
        Starts looping if at least one blue contour or centre is
        found in the frame
        """
        if len(blue_contour) > 0:
            # for creating a circular contour with centroid
            c = max(blue_contour, key=cv2.contourArea)
            ((x, y), r) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            # below is formula for calculating centroid of circle
            centre2 = (int(M["m10"] / (M["m00"] + 0.000001)), int(M["m01"] / (M["m00"] + 0.000001)))

            # if the radius meets a minimum size to avoid small distraction of same color then mark it in frame
            if r > radius_of_circle:
                # draw the circle and centroid on the frame,
                cv2.circle(grabbed_frame, (int(x), int(y)), int(r),
                           (0, 255, 0), 2)
                cv2.circle(grabbed_frame, centre2, 5, (0, 255, 0), -1)
                a.put("SPACE")

        """
        Starts looping if at least one green contour or centre is
        found in the frame"""
        if len(green_contour) > 0:
            # for creating a circular contour with centroid
            c = max(green_contour, key=cv2.contourArea)
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

                # Set a relative centre from which a relative angle will be detected
                centre_angle = angle(center_of_frame, centre)

                """
                Relative angle between 45 and 145 -> Object on the 'Up' section
                Relative angle between 145 and 215 -> Object on the 'Right' section
                Relative angle between -40 and 40 -> Object on the 'Left' section
                'Down' section is awkward, so we defined two different threshholds for the relative angle
                """
                if 45 < centre_angle < 145:
                    cv2.putText(grabbed_frame, 'arriba', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                    #pyautogui.press('up')
                    a.put("UP")
                    #print("up")
                    #current_key.add(up)
                    keyPressed = True
                elif 145 < centre_angle < 215:
                    cv2.putText(grabbed_frame, 'derecha', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                    #pyautogui.press('right')
                    #print("Right")
                    a.put("RIGHT")
                    #current_key.add(right)
                    keyPressed = True
                elif 215 < centre_angle or centre_angle < -40:
                    cv2.putText(grabbed_frame, 'abajo', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                    #yautogui.press('down')
                    #print("Down")
                    a.put("DOWN")
                    #current_key.add(down)
                    keyPressed = True
                elif -40 < centre_angle < 40:
                    cv2.putText(grabbed_frame, 'izquierda', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                    #pyautogui.press('left')
                    #print("Left")
                    a.put("LEFT")
                    #current_key.add(left)
                    keyPressed = True
                # cv2.putText(grabbed_frame, str(centre_angle), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)
                # cv2.putText(grabbed_frame, str(centre), (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (136, 8, 8), 2)

        """
        Below code will show the window through which you can see
        the detection of your object
        """
        grabbed_frame_copy = grabbed_frame.copy()
        """
        Below code is for creating the blue rectangular box
            we should recycle this to draw the direction threshholds
        """
        grabbed_frame_copy = cv2.rectangle(grabbed_frame_copy, (0, height // 2 - window_size // 2),
                                           (width, height // 2 + window_size // 2), (255, 0, 0), 2)
        cv2.imshow("grabbed_frame", grabbed_frame_copy)

        # Release all pressed keys to avoid any glitch
        if not keyPressed and current_key != 0:
            for key in current_key:
                if key != "space":
                    #ReleaseKey(key)
                    current_key = set()
        
        # We don't know why, but appartently the absense of this line will crash the Camera Detection Window
        k = cv2.waitKey(1) & 0xFF
        
        if not b.empty():
            if b.get() == "END":
                break
    return

def main():
    """
    Main function for game initialization
        Parameters
        ----------
        CLOCK: (class) CLOCK
            pygame clock to run the game
        SCREEN: (module) display
            pygame module for game visualization
        FONT: (module) font
            pygame module for message visualization
    """
    global CLOCK, SCREEN, FONT

    pygame.init()
    CLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((Width_window, height_window))
    FONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Snake Game')

    showStartScreen()
    while True:
        runGame()

        showGameOverScreen()


def runGame():
    """
    Main function for game control and execution
        Parameters
        ----------
        startx: int
            Random starting horizontal position
        starty: int
            Random starting vertical position
        worm: list
            Player's position
        FPS: int
            Ingame frames per second
        FPS_trigger: boolean
            Designated Boolean for game acceleration
        direction: variable
            Snake's facing direction
        food: dict[str, int]
            Location of the snake's food
    """
    startx = random.randint(5, cell_width - 6)
    starty = random.randint(5, cell_height - 6)
    global worm
    global FPS
    worm = [{'x': startx, 'y': starty}, {'x': startx - 1, 'y': starty}, {'x': startx - 2, 'y': starty}]
    direction = UP

    food = getRandomLocation()

    global Global_Event_List

    while True:
        FPS = 2
        Interface()  # get events from camera controller
        for event in Global_Event_List.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()
            elif event.type == pygame.TEXTINPUT:
                if (event.text == ' '):
                    FPS = 5
                    """
                    FPS_trigger = True
            if (event.type == KEYUP):
                if (event.key == K_SPACE):
                    FPS_trigger = False
            if FPS_trigger == True:
                FPS = 8
            elif FPS_trigger == False:
                FPS = 2"""

        # To check Collision with screen edges
        if worm[HEAD]['x'] == -1 or worm[HEAD]['x'] == cell_width or worm[HEAD]['y'] == -1 or worm[HEAD][
            'y'] == cell_height:
            return
        # To check Collision with snake's body
        for wormBody in worm[1:]:
            if wormBody['x'] == worm[HEAD]['x'] and wormBody['y'] == worm[HEAD]['y']:
                return
        # Check Collision with food
        if worm[HEAD]['x'] == food['x'] and worm[HEAD]['y'] == food['y']:

            food = getRandomLocation()
        else:
            del worm[-1]

        # To move the Snake
        if direction == UP:
            newHead = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] + 1}
        elif direction == RIGHT:
            newHead = {'x': worm[HEAD]['x'] + 1, 'y': worm[HEAD]['y']}
        elif direction == LEFT:
            newHead = {'x': worm[HEAD]['x'] - 1, 'y': worm[HEAD]['y']}
        worm.insert(0, newHead)

        # For drawing the game Screen
        SCREEN.fill(BGCOLOR)
        drawGrid()
        drawWorm(worm)
        drawfood(food)
        drawScore((len(worm) - 3) * 10)
        pygame.display.update()
        CLOCK.tick(FPS)


def getTotalScore():
    """
    Calculates the game's score based on the snake's length
    """
    return ((len(worm) - 3) * 10)


def drawPressKeyMsg():
    """
    Game's start screen
        Parameters
        ----------
        pressKeyText: Surface
            Font and text on the game's start screen
        pressKeyRect: Rect
            Location of text on the game's start screen
    """
    pressKeyText = FONT.render('Tap to play', True, GREEN)
    pressKeyRect = pressKeyText.get_rect()
    pressKeyRect.center = (Width_window - 200, height_window - 100)
    SCREEN.blit(pressKeyText, pressKeyRect)

def checkForKeyPress():
    """
    Handler that checks for any key being pressed or released
        Parameters
        ----------
        keyUpEvents: list[int]
            List of pygame events
        Returns
        -------
        key: Any
            Key being pressed or released
    """
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    """
    Shows the game's start screen
        Parameters
        ----------
        titlefont: Font
            Font of the game's start screen
        titleText: Surface
            Text on the game's start screen
        titleTextRect:
            Location of text on the game's start screen
    """
    titlefont = pygame.font.Font('freesansbold.ttf', 100)
    titleText = titlefont.render('SNAKE GAME', True, RED)
    while True:
        SCREEN.fill(BGCOLOR)
        titleTextRect = titleText.get_rect()
        titleTextRect.center = (Width_window / 2, height_window / 2)
        SCREEN.blit(titleText, titleTextRect)

        drawPressKeyMsg()
        if checkForKeyPress():
            pygame.event.get()
            return
        pygame.display.update()
        CLOCK.tick(FPS)


def terminate():
    """
    Terminates the game
    """
    pygame.quit()
    global b
    b.put("END")
    sys.exit()


def getRandomLocation():
    """
    Gets a random location for new food
        Returns
        -------
        Set{int,int}
            Random coordinates for new food
    """
    return {'x': random.randint(0, cell_width - 1), 'y': random.randint(0, cell_height - 1)}


def showGameOverScreen():
    """
    Shows game over screen upon death
        Parameters
        ----------
        gameOverFont: Font
            Font of 'game over' text
        gameOverText: Surface
            'game over' text
        gameOverRect: Rect
            Location of 'game over' text on the screen
        totalscoreFont: Font
            Font of 'total score' text
        totalscoreText: Surface
            'total score' text
        totalscoreRect: Rect
            Location of 'total score' text on screen
    """
    gameOverFont = pygame.font.Font('freesansbold.ttf', 100)
    gameOverText = gameOverFont.render('Game Over', True, GREEN)
    gameOverRect = gameOverText.get_rect()
    totalscoreFont = pygame.font.Font('freesansbold.ttf', 40)
    totalscoreText = totalscoreFont.render(f'Total Score: {getTotalScore()}', True, YELLOW)

    totalscoreRect = totalscoreText.get_rect()
    totalscoreRect.midtop = (Width_window / 2, 150)
    gameOverRect.midtop = (Width_window / 2, 30)
    SCREEN.fill(BGCOLOR)
    SCREEN.blit(gameOverText, gameOverRect)
    SCREEN.blit(totalscoreText, totalscoreRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(1000)
    checkForKeyPress()

    while True:
        if checkForKeyPress():
            pygame.event.get()
            return


def drawScore(score):
    """ 
    Shows the game's total score
        Parameters
        ----------
        gameOverText: Surface
            'Total score' text
        gameOverRect: Rect
            Location of 'Total score' text on the screen
    """
    scoreText = FONT.render(f'Score: {score}', True, GREEN)
    scoreRect = scoreText.get_rect()
    scoreRect.center = (Width_window - 100, 30)
    SCREEN.blit(scoreText, scoreRect)


def drawWorm(worm):
    """ 
    Draws the Snake on screen
        Parameters
        ----------
        x: Any
            Horizontal position of the snake
        y: Any
            Vertical position of the snake
    """
    x = worm[HEAD]['x'] * size_cell
    y = worm[HEAD]['y'] * size_cell
    wormHeadRect = pygame.Rect(x, y, size_cell, size_cell)
    pygame.draw.rect(SCREEN, DARKGRAY, wormHeadRect)

    for coord in worm[1:]:
        x = coord['x'] * size_cell
        y = coord['y'] * size_cell
        wormSegmentRect = pygame.Rect(x, y, size_cell, size_cell)
        pygame.draw.rect(SCREEN, RED, wormSegmentRect)


def drawfood(coord):
    """ 
    Draws the Food on screen
        Parameters
        ----------
        x: Any
            Horizontal position of the Food
        y: Any
            Vertical position of the Food
    """
    x = coord['x'] * size_cell
    y = coord['y'] * size_cell
    appleRect = pygame.Rect(x, y, size_cell, size_cell)
    pygame.draw.rect(SCREEN, DARKGREEN, appleRect)


def drawGrid():
    """ 
    Draws the Grid on screen
    """
    for x in range(0, Width_window, size_cell):
        pygame.draw.line(SCREEN, RED, (x, 0), (x, height_window))
    for y in range(0, height_window, size_cell):
        pygame.draw.line(SCREEN, RED, (0, y), (Width_window, y))





def Interface():
    """
    Links events between Camera_Detection and the Game's processes
        Parameters
        ----------
        'a': Queue
            Recieved information from Camera_Detection
        Global_Event_List: type:alias
            List of pygame global events
        a_content: List
            List of 'a' contents as cache
    """
    global a
    global Global_Event_List

    a_content = []
    while not a.empty():
        a_content.append(a.get())
    for instruction in a_content:
        if instruction == "UP":
            #add keydown type
            Global_Event_List.post(pygame.event.Event(pygame.KEYDOWN, {'unicode': '', 'key': 1073741906, 'mod': 0, 'scancode': 82, 'window': None}))

            #pygame.event.post()
        elif instruction == "DOWN":
            Global_Event_List.post(pygame.event.Event(pygame.KEYDOWN, {'unicode': '', 'key': 1073741905, 'mod': 0, 'scancode': 81, 'window': None}))

            #pygame.event.post(K_DOWN)
        elif instruction == "LEFT":
            #pygame.event.post()
            Global_Event_List.post(pygame.event.Event(pygame.KEYDOWN, {'unicode': '', 'key': 1073741904, 'mod': 0, 'scancode': 80, 'window': None}))
        elif instruction == "RIGHT":
            #pygame.event.post()
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'unicode': '', 'key': 1073741903, 'mod': 0, 'scancode': 79, 'window': None}))
        elif instruction == "SPACE":
            #pygame.event.post()
            Global_Event_List.post(pygame.event.Event(pygame.TEXTINPUT, {'text': ' ', 'window': None}))
    return




if __name__ == '__main__':

    a = mp.Queue()
    b = mp.Queue()
    p = mp.Process(target=Camera_Detection, args=(a,b))
    p.start()

    Global_Event_List = pygame.event

    while not b.empty():
        print("Waiting for camera")
        print(b.get()) #cam ready signal

    main()
