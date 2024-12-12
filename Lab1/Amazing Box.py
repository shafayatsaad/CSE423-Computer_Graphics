#Task2

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Global variables to manage point generation, movement, and state
points = []
speed = 0.01
freeze = False

class Point:
    def __init__(self, x, y):
        # Task 2(i): Initialize point with random color and diagonal movement
        self.x = x
        self.y = y
        self.color = [random.random(), random.random(), random.random()]
        self.original_color = self.color.copy()
        # Random diagonal movement in 4 possible directions
        diagonal = random.choice([(1,1), (1,-1), (-1,1), (-1,-1)])
        self.dx = diagonal[0]
        self.dy = diagonal[1]
        self.blink_start = 0
        self.blinking = False

    def update(self):
        # Task 2(i): Implement point movement and boundary bouncing
        if not freeze:
            # Bounce off window boundaries by reversing direction
            if self.x <= 0 or self.x >= 500:
                self.dx *= -1
            if self.y <= 0 or self.y >= 500:
                self.dy *= -1
            
            # Move point based on current speed
            self.x += self.dx * speed
            self.y += self.dy * speed

            # Task 2(iii): Blinking point mechanism
            if self.blinking:
                elapsed = time.time() - self.blink_start
                if elapsed <= 1.0:
                    # Toggle between background color and original color
                    self.color = [0,0,0] if elapsed % 0.5 < 0.25 else self.original_color.copy()
                else:
                    # Reset blinking state after 1 second
                    self.blinking = False
                    self.color = self.original_color.copy()

def draw_point(point):
    # Render individual point
    glPointSize(5)
    glBegin(GL_POINTS)
    glColor3f(*point.color)
    glVertex2f(point.x, point.y)
    glEnd()

def mouse(button, state, x, y):
    # Task 2(i) & (iii): Handle mouse button events
    if freeze:
        return
        
    y = 500 - y  # Convert coordinates to OpenGL system
    
    # Task 2(i): Right-click generates random moving points
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        points.append(Point(x, y))
        
    # Task 2(iii): Left-click makes points blink
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        now = time.time()
        for p in points:
            p.blinking = True
            p.blink_start = now

def special(key, x, y):
    # Task 2(ii): Change point speed with arrow keys
    global speed
    if not freeze:
        if key == GLUT_KEY_UP:
            speed *= 1.5
        if key == GLUT_KEY_DOWN:
            speed /= 1.5

def keyboard(key, x, y):
    # Task 2(iv): Freeze/unfreeze points with spacebar
    global freeze
    if key == b' ':
        freeze = not freeze

def display():
    # Render and update points in each frame
    glClear(GL_COLOR_BUFFER_BIT)
    for point in points:
        point.update()
        draw_point(point)
    glutSwapBuffers()

def init():
    # Initialize OpenGL viewport and projection
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 500, 0, 500, 0, 1)

# GLUT initialization and main loop
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(500, 500)
glutCreateWindow(b"Amazing Box")
init()
glutDisplayFunc(display)
glutMouseFunc(mouse)
glutSpecialFunc(special)
glutKeyboardFunc(keyboard)
glutIdleFunc(display)
glutMainLoop()