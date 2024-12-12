from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# Task 1: Building a House in Rainfall
# Global Variables for rainfall and environment
raindrops = []
night_mode = False
rain_direction = 0
background_color = 1.0  # Daytime initially

# Task 1(i): Initialize raindrops for animation
for i in range(100):
    x = random.randint(0, 500)
    y = random.randint(500, 800)
    raindrops.append((x, y))

def rain():
    # Task 1(i): Animate raindrops falling from top to bottom
    global raindrops, rain_direction
    speed = 0.5
    for i, (x, y) in enumerate(raindrops):
        new_y = y - speed
        if new_y < 100:
            new_y = 500
        raindrops[i] = (x, new_y)
    glutPostRedisplay()

def show_raindrops():
    # Task 1(i) & (ii): Render raindrops with directional control
    global raindrops
    for x, y in raindrops:
        glLineWidth(2)
        glBegin(GL_LINES)
        glColor3f(0.0, 0.0, 1.0)
        glVertex2f(x, y)
        glVertex2f(x + rain_direction, y - 10)
        glEnd()

def draw_points(x, y):
    glPointSize(5)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_lines(x1, y1, x2, y2, w):
    glLineWidth(w)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

def draw_roof(x1, y1, x2, y2, x3, y3, w):
    # Task 1(i): Draw roof using only lines (no fill)
    glColor3f(0.5, 0.0, 0.0)
    draw_lines(x1, y1, x2, y2, w)
    draw_lines(x2, y2, x3, y3, w)
    draw_lines(x3, y3, x1, y1, w)

def draw_house():
    draw_roof(100, 250, 400, 250, 250, 350, w=15)
    draw_base()

def draw_base():
    draw_basement(150, 250, 145, 100, 355, 100, 350, 250, w=10)
    draw_door(180, 100, 180, 180, 230, 180, 230, 100, w=5)
    draw_window(280, 185, 280, 225, 320, 225, 320, 185, w=3)

def draw_basement(x1, y1, x2, y2, x3, y3, x4, y4, w):
    draw_lines(x1, y1, x2, y2, w)
    draw_lines(x2 - 20, y2, x3 + 20, y3, w)
    draw_lines(x3, y3, x4, y4, w)
    draw_lines(x4, y4, x1, y1, w)

def draw_door(x1, y1, x2, y2, x3, y3, x4, y4, w):
    draw_lines(x1, y1, x2, y2 + 3, w)
    draw_lines(x2, y2, x3, y3, w)
    draw_lines(x3, y3 + 3, x4, y4, w)
    draw_lines(x4, y4, x1, y1, w)
    draw_points(215, 140)

def draw_window(x1, y1, x2, y2, x3, y3, x4, y4, w):
    draw_lines(x1, y1 - 5, x2, y2 + 5, w)
    draw_lines(x2 - 5, y2, x3 + 5, y3, w)
    draw_lines(x3, y3 + 5, x4, y4 - 5, w)
    draw_lines(x4 + 5, y4, x1 - 5, y1, w)
    # Window grid lines
    draw_lines(280, 195, 320, 195, w=2)
    draw_lines(280, 215, 320, 215, w=2)
    draw_lines(300, 225, 300, 185, w=2)
    draw_lines(290, 225, 290, 185, w=2)
    draw_lines(310, 225, 310, 185, w=2)

def iterate():
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    # Main display function
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    global background_color

    # Task 1(iii): Background color management
    background_color = max(0.0, min(1.0, background_color))
    glClearColor(background_color, background_color, background_color, background_color)
    glClear(GL_COLOR_BUFFER_BIT)
    iterate()

    show_raindrops()
    glColor3f(0.5, 0.0, 0.0)
    draw_house()
    glutSwapBuffers()

def key_pressed(key, x, y):
    # Task 1(iii): Day/Night color transition
    global night_mode, background_color
    if key == b'n':
        night_mode = True
        background_color = max(0.0, background_color - 0.1)
    elif key == b'd':
        night_mode = False
        background_color = min(1.0, background_color + 0.1)
    glutPostRedisplay()

def specialKeyListener(key, x, y):
    # Task 1(ii): Rain direction control
    global rain_direction
    if key == GLUT_KEY_LEFT:
        rain_direction -= 1
    elif key == GLUT_KEY_RIGHT:
        rain_direction += 1
    glutPostRedisplay()

def init():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, 1, 1, 1000.0)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(500, 500)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Rainy House")
    glutDisplayFunc(showScreen)

    glutIdleFunc(rain)
    glutKeyboardFunc(key_pressed)
    glutSpecialFunc(specialKeyListener)

    glutMainLoop()

if __name__ == "__main__":
    main()
