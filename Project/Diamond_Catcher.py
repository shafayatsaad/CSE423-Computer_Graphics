from OpenGL.GL import *
from OpenGL.GLUT import *
import math
import random

# Constants
LEVEL_3_THRESHOLD = 9
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 650
DIAMOND_SIZE = 15
BOWL_WIDTH = 100
BOWL_HEIGHT = 30
DIAMOND_FALL_SPEED = 2.5
BOWL_SPEED = 4.0  # Adjust the bowl movement speed
LEVEL_2_THRESHOLD = 60
# Colors
WHITE = (1, 1, 1)
RED = (1, 0, 0)
YELLOW = (1, 1, 0)
BLUE = (0, 0, 1)
TEAL = (0, 1, 1)
AMBER = (1, 0.75, 0)
BLACK = (0, 0, 0)

# Initialize variables
diamonds_caught = 0
missed_diamonds = 0
points = 0
game_paused = False
game_over = False

bowl_x = SCREEN_WIDTH // 2 - BOWL_WIDTH // 2
bowl_y = 10

diamonds = []

restart_button_clicked = False
pause_button_clicked = False
exit_button_clicked = False
power_up_active = False
# Define the button coordinates and dimensions
button_width = 50
button_height = 50
button_spacing = 10

restart_button_x = button_spacing
restart_button_y = SCREEN_HEIGHT - button_height - button_spacing
pause_button_x = SCREEN_WIDTH // 2 - button_width // 2
pause_button_y = SCREEN_HEIGHT - button_height - button_spacing
exit_button_x = SCREEN_WIDTH - button_width - button_spacing
exit_button_y = SCREEN_HEIGHT - button_height - button_spacing

# Collision Class


class AABB:
    x = 0
    y = 0
    w = 0
    h = 0

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def collides_with(self, other):
        return (
            self.x < other.x + other.w and
            self.x + self.w > other.x and
            self.y < other.y + other.h and
            self.y + self.h > other.y
        )


# Global variables
bowl_aabb = AABB(bowl_x, bowl_y, BOWL_WIDTH, BOWL_HEIGHT)
collision = False

restart_button_aabb = AABB(
    restart_button_x, restart_button_y, button_width, button_height)
pause_button_aabb = AABB(pause_button_x, pause_button_y,
                         button_width, button_height)
exit_button_aabb = AABB(exit_button_x, exit_button_y,
                        button_width, button_height)

# Define game state


def start_game():
    global diamonds_caught, missed_diamonds, points, diamonds, game_paused, game_over
    diamonds_caught = 0
    missed_diamonds = 0
    points = 0
    diamonds.clear()
    game_paused = False
    game_over = False

# Draw button shapes


def draw_line(x1, y1, x2, y2):
    # Midpoint line drawing algorithm
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    x = x1
    y = y1

    glVertex2f(x, y)  # Start the line here

    while x <= x2:
        x += 1
        if d < 0:
            d += 2 * dy
        else:
            d += 2 * (dy - dx)
            y += 1
        glVertex2f(x, y)  # Add points to the line here


def draw_button(x, y, width, height, color):
    glBegin(GL_POINTS)
    glColor3f(*color)

    # Draw top horizontal line
    draw_line(x, y, x + width, y)

    # Draw bottom horizontal line
    draw_line(x, y + height, x + width, y + height)

    # Draw left vertical line
    draw_line(x, y, x, y + height)

    # Draw right vertical line
    draw_line(x + width, y, x + width, y + height)

    glEnd()


def egg(x, y, radius):
    global power_up_active  # Declare it as a global variable

    glBegin(GL_POINTS)
    if power_up_active:
        glColor3f(1.0, 1.0, 0.0)  # Yellow for eggs during power-up
        radius *= 1.5  # Increase the size during power-up
    else:
        glColor3f(1.0, 1.0, 0.0)  # Regular yellow for eggs

    num_segments = 100
    x_center, y_center = x, y

    x1, y1 = radius, 0

    # Initial decision parameter of the region 1
    P = 1 - radius

    while x1 > y1:
        # Increment angle by 45 degrees for eight-way symmetry
        x1 -= 1
        y1 += 1

        # Check if the decision parameter is less than 0
        if P <= 0:
            P = P + 2 * y1 + 1
        else:  # Adjust parameters for region 2
            x1 += 1
            P = P + 2 * (y1 - x1) + 1

        # Use symmetry to draw all eight points
        glVertex2f(x_center + x1, y_center + y1)
        glVertex2f(x_center - x1, y_center + y1)
        glVertex2f(x_center + x1, y_center - y1)
        glVertex2f(x_center - x1, y_center - y1)
        glVertex2f(x_center + y1, y_center + x1)
        glVertex2f(x_center - y1, y_center + x1)
        glVertex2f(x_center + y1, y_center - x1)
        glVertex2f(x_center - y1, y_center - x1)

    glEnd()


def diamond_start():
    return random.uniform(DIAMOND_SIZE, SCREEN_WIDTH - DIAMOND_SIZE), SCREEN_HEIGHT


def diamond(x, y):
    egg(x, y, DIAMOND_SIZE)


def midpoint_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    x = x1
    y = y1

    glBegin(GL_POINTS)

    while x <= x2:
        glVertex2f(x, y)
        x += 1
        if d < 0:
            d += 2 * dy
        else:
            d += 2 * (dy - dx)
            y += 1

    glEnd()


def draw_bowl():
    global bowl_x, bowl_y, BOWL_WIDTH, BOWL_HEIGHT, RED, YELLOW, power_up_active, diamonds_caught, points

    if power_up_active:
        glColor3f(*YELLOW)  # Yellow for the box during power-up
        BOWL_WIDTH = 120  # Increase the width during power-up
        BOWL_HEIGHT = 40  # Increase the height during power-up
    else:
        glColor3f(*RED)  # Regular red for the box

    # Draw rounded rectangle for the bowl using midpoint line drawing algorithm
    draw_rounded_rectangle(bowl_x, bowl_y, BOWL_WIDTH, BOWL_HEIGHT, 10)

    # Decrease the width of the bowl after catching more than 5 diamonds
    if diamonds_caught > 5:
        BOWL_WIDTH = max(60, BOWL_WIDTH - 2)

    # Display Level 2 under the score when bowl size gets smaller
    if BOWL_WIDTH <= LEVEL_2_THRESHOLD:
        glColor3f(1.0, 1.0, 1.0)
        draw_text(10, SCREEN_HEIGHT - 180, "Level 2")

    # Display Level 3 under the score when catching 9 eggs
    if diamonds_caught >= LEVEL_3_THRESHOLD:
        glColor3f(1.0, 1.0, 1.0)
        draw_text(10, SCREEN_HEIGHT - 200, "Level 3")


def draw_rounded_rectangle(x, y, width, height, radius):
    num_segments = 100
    glBegin(GL_POINTS)

    # Draw top horizontal line
    draw_midpoint_line(x + radius, y + height, x + width - radius, y + height)

    # Draw bottom horizontal line
    draw_midpoint_line(x + radius, y, x + width - radius, y)

    # Draw left vertical line
    draw_midpoint_line(x, y + radius, x, y + height - radius)

    # Draw right vertical line
    draw_midpoint_line(x + width, y + radius, x + width, y + height - radius)

    # Draw top-left arc
    draw_arc(x + radius, y + height - radius, radius, 180, 270)

    # Draw top-right arc
    draw_arc(x + width - radius, y + height - radius, radius, 270, 360)

    # Draw bottom-left arc
    draw_arc(x + radius, y + radius, radius, 90, 180)

    # Draw bottom-right arc
    draw_arc(x + width - radius, y + radius, radius, 0, 90)

    glEnd()

# Helper function for drawing a circular arc using midpoint line drawing algorithm


def draw_arc(center_x, center_y, radius, start_angle, end_angle):
    num_segments = 100
    angle_step = 360 / num_segments

    for i in range(int(start_angle), int(end_angle), int(angle_step)):
        x = center_x + radius * math.cos(math.radians(i))
        y = center_y + radius * math.sin(math.radians(i))
        glVertex2f(x, y)

# Helper function for drawing a midpoint line


def draw_midpoint_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    x = x1
    y = y1

    while x <= x2:
        x += 1
        if d < 0:
            d += 2 * dy
        else:
            d += 2 * (dy - dx)
            y += 1
        glVertex2f(x, y)


def draw_restart_button():
    global restart_button_clicked, power_up_active

    x = restart_button_x
    y = restart_button_y

    glColor3f(*TEAL)  # TEAL color for the button

    midpoint_line(x, y, x + button_width, y)
    midpoint_line(x, y + button_height, x + button_width, y + button_height)

    glColor3f(*WHITE)  # BLACK color for the text
    draw_text(x + 10, y + 15, "RESTART")

    # Toggle power-up state when the button is clicked
    if restart_button_clicked:
        power_up_active = not power_up_active
        restart_button_clicked = False


def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


def draw_pause_button():
    x = pause_button_x
    y = pause_button_y

    glColor3f(*AMBER)

    # Draw pause shape
    midpoint_line(x, y, x + button_width, y)
    midpoint_line(x, y + button_height, x + button_width, y + button_height)

    glColor3f(*WHITE)
    if game_paused:
        draw_text(x + 20, y + 15, "PLAY")
    else:
        draw_text(x + 15, y + 15, "PAUSE")


def draw_exit_button():
    x = exit_button_x
    y = exit_button_y

    glColor3f(*RED)

    # Draw 'X' shape
    midpoint_line(x, y + button_height, x + button_width, y + button_height)
    midpoint_line(x, y, x + button_width, y)

    glColor3f(*WHITE)
    draw_text(x + 13, y + 15, "EXIT")


def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


def check_collision():
    global bowl_aabb, diamonds, diamonds_caught, missed_diamonds, points, collision, game_over, power_up_active

    for i in range(len(diamonds)):
        diamond_aabb = AABB(
            diamonds[i][0], diamonds[i][1], DIAMOND_SIZE, DIAMOND_SIZE)
        if bowl_aabb.collides_with(diamond_aabb):
            diamonds_caught += 1
            points += 10
            diamonds.pop(i)
            collision = True

            # Reset power-up state after catching the special egg
            if diamonds_caught > 6:
                power_up_active = False

            return

    # Check for missed diamonds
    for i in range(len(diamonds)):
        if diamonds[i][1] < 0:
            missed_diamonds += 1
            if missed_diamonds >= 1:
                game_over = True

                # Reset power-up state on game over
                power_up_active = False

                return


def display():
    global collision, game_over
    glClear(GL_COLOR_BUFFER_BIT)
    for diamond_x, diamond_y in diamonds:
        diamond(diamond_x, diamond_y)
    draw_bowl()
    draw_restart_button()
    draw_pause_button()
    draw_exit_button()
    check_collision()
    if game_over:
        glColor3f(1.0, 0.0, 0.0)
        draw_text(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2, "Game Over")
    else:
        if collision:
            glColor3f(1.0, 0.0, 0.0)
        else:
            glColor3f(0.0, 1.0, 0.0)

    # Display the score
    draw_text(10, SCREEN_HEIGHT - 150,
              "Diamonds Caught: " + str(diamonds_caught))

    glutSwapBuffers()


def update(value):
    global diamonds_caught, missed_diamonds, points, game_paused, bowl_x, BOWL_SPEED, power_up_active, DIAMOND_FALL_SPEED

    if not game_paused and not game_over:
        if len(diamonds) < 1:
            diamonds.append(diamond_start())

        for i in range(len(diamonds)):
            diamonds[i] = (diamonds[i][0], diamonds[i][1] - DIAMOND_FALL_SPEED)

            if diamonds[i][0] >= bowl_x and diamonds[i][0] <= bowl_x + BOWL_WIDTH and diamonds[i][1] <= bowl_y:
                diamonds_caught += 1
                points += 10
                diamonds.pop(i)

        # Adjust egg falling speed after catching 8 diamonds
        if diamonds_caught > 6:
            DIAMOND_FALL_SPEED = 4.0

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


def reset_game():
    global diamonds_caught, missed_diamonds, points, diamonds, collision, game_paused, game_over
    diamonds_caught = 0
    missed_diamonds = 0
    points = 0
    diamonds.clear()
    game_paused = False
    game_over = False


def special(key, x, y):
    global bowl_x, BOWL_SPEED

    # Handle arrow key events to move the bowl left and right
    if key == GLUT_KEY_LEFT:
        bowl_x -= BOWL_SPEED
    elif key == GLUT_KEY_RIGHT:
        bowl_x += BOWL_SPEED

    # Ensure the bowl stays within the screen bounds
    bowl_x = max(0, min(SCREEN_WIDTH - BOWL_WIDTH, bowl_x))

# Handle mouse clicks


def mouse(button, state, x, y):
    global restart_button_clicked, pause_button_clicked, exit_button_clicked, game_paused
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if restart_button_aabb.collides_with(AABB(x, SCREEN_HEIGHT - y, 0, 0)):
            print("Starting Over")
            reset_game()
            diamonds.append(diamond_start())
        elif pause_button_aabb.collides_with(AABB(x, SCREEN_HEIGHT - y, 0, 0)):
            game_paused = not game_paused
        elif exit_button_aabb.collides_with(AABB(x, SCREEN_HEIGHT - y, 0, 0)):
            print("Goodbye")
            glutLeaveMainLoop()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutCreateWindow(b"Diamond Catching Game")
    glutDisplayFunc(display)
    glutMouseFunc(mouse)
    glutSpecialFunc(special)  # Register the special function for arrow keys
    glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)
    start_game()
    glutTimerFunc(16, update, 0)

    glutMainLoop()


if __name__ == "__main__":
    main()

