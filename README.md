# CV-Snake
Snake game in pygame instructions.

## How to run the code:
In order to play the game you need to either install the following pygame libraries and run SnakeGame.py:
- pygame
- cv2
- numpy

Or download and run the poetry files

Executing "run.sh" also creates the necessaary enviroment and runs the game

After installing the game you need to have a camera plugged in before running it.
Be sure you don´t have noticeable blue or green objects on the background, otherwise the game might detect them as input
If you don´t have a camera, you can always play with your keyboard

How to Play: 
1) Press any arrow key on the keyboard to start. 
2) Take and move a green object on your camera to direct the snake to the desired destination
   -  Move it up and the snake will follow the "up" direction, move it down so that the snake will turn "down", move the object left so that the snake turns "left" and move it right so that the snake goes "right".
   - The keyboard equivalent for this direction controls are the arrow keys
3) Take and display a blue object anywhere on camera for the snake to accelerate its movement. Take the blue object out of camera to return to normal speed
   - The keyboard equivalent for acceleration controls is the spacebar. Press the spacebar to accelerate and release it to return to normal speed
4) You can combine direction controls and acceleration with both objects at the same time.
5) Press "ESC" or close the snake window to close the game and the camera detection window

>Written by Lucas Rifo and Christopher Pavez
