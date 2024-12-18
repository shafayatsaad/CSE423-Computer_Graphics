import math
import sys
import random
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SHOOTER_SPEED = 10
BULLET_SPEED = 5
INITIAL_FALLING_CIRCLE_SPEED = 0.5
SPEED_INCREMENT = 0.05
UNIQUE_CIRCLE_SPEED_INCREMENT = 0.1
BULLET_RADIUS = 5
SHOOTER_WIDTH = 30
SHOOTER_HEIGHT = 40
FALLING_CIRCLE_RADIUS = 20
LIVES = 3
MAX_MISFIRES_ALLOWED = 4
UNIQUE_CIRCLE_POINTS = 5

shooter_position = WINDOW_WIDTH // 2
bullets = []
falling_circles = []
score = 0
lives = LIVES
misfires = 0
game_over = False
game_paused = False
falling_circle_speed = INITIAL_FALLING_CIRCLE_SPEED
exit_game = False

class FallingCircle:
    def __init__(self, x, y, radius, radius_change_rate, radius_change_direction, is_unique):
        self.x = x
        self.y = y
        self.radius = radius
        self.radius_change_rate = radius_change_rate
        self.radius_change_direction = radius_change_direction
        self.is_unique = is_unique

def draw_point(x, y):
    glVertex2f(x, y)

def draw_spaceship_points(x, y):
    # Draw spaceship body (triangle) using points
    # Top point
    for dx in range(-SHOOTER_WIDTH//2, SHOOTER_WIDTH//2 + 1):
        draw_point(x + dx, y + SHOOTER_HEIGHT)
    
    # Bottom line
    for dx in range(-SHOOTER_WIDTH//2, SHOOTER_WIDTH//2 + 1):
        draw_point(x + dx, y)
    
    # Cockpit
    for dx in range(-SHOOTER_WIDTH//4, SHOOTER_WIDTH//4 + 1):
        draw_point(x + dx, y + SHOOTER_HEIGHT + 10)

def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(char))

def draw_button_points(x, y, width, height):
    # Draw button outline using points
    # Horizontal lines
    for dx in range(width + 1):
        draw_point(x + dx, y)
        draw_point(x + dx, y + height)
    
    # Vertical lines
    for dy in range(height + 1):
        draw_point(x, y + dy)
        draw_point(x + width, y + dy)

def draw_back_icon_points(x, y, size):
    # Horizontal line
    for dx in range(-size, size + 1):
        draw_point(x + dx, y)
    
    # Arrow points
    draw_point(x - size, y)
    draw_point(x - size/2, y + size)
    draw_point(x - size/2, y - size)

def draw_play_icon_points(x, y, size):
    # Draw play triangle using points
    for dx in range(-size, size + 1):
        draw_point(x - size, y + dx)
        draw_point(x, y)
        draw_point(x + size, y + dx)

def draw_pause_icon_points(x, y, size):
    # Draw pause bars using points
    # Left bar
    for dx in range(size//2 + 1):
        for dy in range(-size, size + 1):
            draw_point(x - size + dx, y + dy)
    
    # Right bar
    for dx in range(size//2 + 1):
        for dy in range(-size, size + 1):
            draw_point(x + size/2 + dx, y + dy)

def draw_cross_icon_points(x, y, size):
    # Diagonal cross lines
    for i in range(-size, size + 1):
        draw_point(x + i, y + i)
        draw_point(x + i, y - i)

def midpoint_circle_draw(xc, yc, radius):
    x = 0
    y = radius
    d = 1 - radius
    while x <= y:
        points = [(xc + x, yc + y), (xc - x, yc + y),
                  (xc + x, yc - y), (xc - x, yc - y),
                  (xc + y, yc + x), (xc - y, yc + x),
                  (xc + y, yc - x), (xc - y, yc - x)]
        for point in points:
            draw_point(*point)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1

def mouse_click(button, state, x, y):
    global game_paused, game_over, exit_game

    y = WINDOW_HEIGHT - y

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Back icon
        if 30 <= x <= 70 and WINDOW_HEIGHT - 70 <= y <= WINDOW_HEIGHT - 30:
            restart_game()

        # Play/Pause icon
        elif WINDOW_WIDTH // 2 - 20 <= x <= WINDOW_WIDTH // 2 + 20 and WINDOW_HEIGHT - 70 <= y <= WINDOW_HEIGHT - 30:
            game_paused = not game_paused

        # Close icon
        elif WINDOW_WIDTH - 70 <= x <= WINDOW_WIDTH - 30 and WINDOW_HEIGHT - 70 <= y <= WINDOW_HEIGHT - 30:
            exit_game = True

def keyboard(key, x, y):
    global shooter_position, bullets, game_over, game_paused, score, misfires, exit_game
    if key == b'a' and not game_paused and not game_over:
        shooter_position = max(SHOOTER_WIDTH/2, shooter_position - SHOOTER_SPEED)
    elif key == b'd' and not game_paused and not game_over:
        shooter_position = min(WINDOW_WIDTH - SHOOTER_WIDTH/2, shooter_position + SHOOTER_SPEED)
    elif key == b' ' and not game_paused and not game_over:
        bullets.append([shooter_position, 50])
    elif key == b'r':
        restart_game()
    elif key == b'p':
        game_paused = not game_paused
    elif key == b'\x1b':  # ESC to quit
        exit_game = True

def restart_game():
    global bullets, falling_circles, score, lives, misfires, game_over, game_paused, falling_circle_speed, shooter_position
    bullets = []
    falling_circles = []
    score = 0
    lives = LIVES
    misfires = 0
    game_over = False
    game_paused = False
    falling_circle_speed = INITIAL_FALLING_CIRCLE_SPEED
    shooter_position = WINDOW_WIDTH // 2
    print("Game restarted. Score and speed reset.")

def create_falling_circle(is_unique=False):
    x = random.randint(FALLING_CIRCLE_RADIUS, WINDOW_WIDTH - FALLING_CIRCLE_RADIUS)
    radius = random.randint(FALLING_CIRCLE_RADIUS, FALLING_CIRCLE_RADIUS * 2)
    radius_change_rate = random.uniform(0.1, 0.5)
    radius_change_direction = 1 if random.random() < 0.5 else -1
    falling_circles.append(FallingCircle(x, WINDOW_HEIGHT, radius, radius_change_rate, radius_change_direction, is_unique))

def update(value):
    global bullets, falling_circles, score, lives, game_over, game_paused, falling_circle_speed, misfires, exit_game

    if exit_game:
        print(f"Goodbye. Final Score: {score}")
        glutDestroyWindow(window_id)
        return

    if not game_paused and not game_over:
        bullets = [[x, y + BULLET_SPEED] for x, y in bullets if y < WINDOW_HEIGHT]

        if random.random() < 0.01:
            create_falling_circle(random.random() < 0.05)

        for circle in falling_circles[:]:
            circle.y -= falling_circle_speed
            if circle.y < 0:
                falling_circles.remove(circle)
                lives -= 1
                if lives == 0:
                    game_over = True
                    print("Game Over: You ran out of lives.")

            # Update unique circle radius
            if circle.is_unique:
                if circle.radius_change_direction == 1:
                    circle.radius = min(circle.radius + circle.radius_change_rate, FALLING_CIRCLE_RADIUS * 2)
                    if circle.radius == FALLING_CIRCLE_RADIUS * 2:
                        circle.radius_change_direction = -1
                else:
                    circle.radius = max(circle.radius - circle.radius_change_rate, FALLING_CIRCLE_RADIUS)
                    if circle.radius == FALLING_CIRCLE_RADIUS:
                        circle.radius_change_direction = 1

            # Collision detection with spaceship
            if (abs(circle.x - shooter_position) < SHOOTER_WIDTH/2 and 
                circle.y < SHOOTER_HEIGHT and circle.y > 0):
                game_over = True
                print("Game Over: Hit by a falling circle.")

        for bullet in bullets[:]:
            for circle in falling_circles[:]:
                distance = math.hypot(bullet[0] - circle.x, bullet[1] - circle.y)
                if distance < BULLET_RADIUS + circle.radius:
                    bullets.remove(bullet)
                    falling_circles.remove(circle)
                    if circle.is_unique:
                        score += UNIQUE_CIRCLE_POINTS
                    else:
                        score += 1
                    if circle.is_unique:
                        falling_circle_speed += UNIQUE_CIRCLE_SPEED_INCREMENT
                    else:
                        falling_circle_speed += SPEED_INCREMENT
                    break

        for bullet in bullets[:]:
            if bullet[1] >= WINDOW_HEIGHT:
                bullets.remove(bullet)
                misfires += 1
                if misfires >= MAX_MISFIRES_ALLOWED:
                    game_over = True
                    print("Game Over: Too many misfires.")

    if not exit_game:
        glutPostRedisplay()
        glutTimerFunc(int(1000/60), update, 0)

def draw():
    global misfires

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)

    # Drawing everything with GL_POINTS
    glBegin(GL_POINTS)
    
    # Spaceship Shooter
    glColor3f(1, 0, 0)
    draw_spaceship_points(shooter_position, 10)

    # Bullets
    glColor3f(0, 1, 0)
    for bullet in bullets:
        midpoint_circle_draw(bullet[0], bullet[1], BULLET_RADIUS)

    # Falling Circles
    for circle in falling_circles:
        if circle.is_unique:
            glColor3f(1, 0, 1)  # Purple color for unique circles
        else:
            glColor3f(0, 0, 1)
        midpoint_circle_draw(circle.x, circle.y, circle.radius)

    glEnd()

    # Text and game over message (points cannot render text, so use bitmap)
    glColor3f(1, 1, 1)
    draw_text(10, WINDOW_HEIGHT - 20, f"Score: {score} Lives: {lives} Misfires: {misfires}")

    if game_over:
        draw_text(WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2, "GAME OVER! Press 'R' to Restart")

    # Draw Icons (Back, Play/Pause, Close)
    glBegin(GL_POINTS)
    glColor3f(1, 1, 1)
    draw_back_icon_points(50, WINDOW_HEIGHT - 50, 20)
    
    if game_paused:
        draw_play_icon_points(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50, 20)
    else:
        draw_pause_icon_points(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50, 20)
    
    draw_cross_icon_points(WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50, 20)
    glEnd()

    glutSwapBuffers()

window_id = None

def init():
    global window_id
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window_id = glutCreateWindow(b'Shoot the Circles Game')
    glutDisplayFunc(draw)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse_click)
    glutTimerFunc(int(1000/60), update, 0)
    glutMainLoop()

if __name__ == '__main__':
    init()
