from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Constants
LIVES = 3
BOMB_SIZE = 15
DIAMONDS_PER_LIFE = 3
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 650
DIAMOND_SIZE = 15
BOWL_WIDTH = 100
BOWL_HEIGHT = 30
BOWL_SPEED = 4.0

# Level-specific constants
LEVEL_THRESHOLDS = [20, 40, 60]  # Points needed for each level
BOMB_SPAWN_RATES = [0.005, 0.01, 0.015, 0.02]  # Spawn rates for each level
DIAMOND_FALL_SPEEDS = [2.0, 2.5, 3.0, 3.5]  # Fall speeds for each level
BOMB_FALL_SPEEDS = [2.5, 3.0, 3.5, 4.0]  # Bomb fall speeds for each level

# Particle effect constants
PARTICLE_COUNT = 20
PARTICLE_LIFETIME = 30
PARTICLE_SPEED = 3.0
TIME_SLOWDOWN_THRESHOLD = 3
TIME_SLOWDOWN_FACTOR = 0.5
TIME_SLOWDOWN_DURATION = 100

# Colors
WHITE = (1, 1, 1)
RED = (1, 0, 0)
YELLOW = (1, 1, 0)
BLUE = (0, 0, 1)
TEAL = (0, 1, 1)
AMBER = (1, 0.75, 0)
BLACK = (0, 0, 0)
GREEN = (0, 1, 0)

# Button Constants
BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50
BUTTON_SPACING = 10

# Initialize variables
diamonds_caught = 0
missed_diamonds = 0
points = 0
game_paused = False
game_over = False
lives = LIVES
ground_diamonds = 0
current_level = 0
particles = []
consecutive_catches = 0
time_slowdown_active = False
time_slowdown_timer = 0
current_time_factor = 1.0

bowl_x = SCREEN_WIDTH // 2 - BOWL_WIDTH // 2
bowl_y = 10

diamonds = []
bombs = []

# Button positions
restart_button_x = BUTTON_SPACING
restart_button_y = SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_SPACING
pause_button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
pause_button_y = SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_SPACING
exit_button_x = SCREEN_WIDTH - BUTTON_WIDTH - BUTTON_SPACING
exit_button_y = SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_SPACING

class AABB:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def collides_with(self, other):
        return (
            self.x < other.x + other.w and
            self.x + self.w > other.x and
            self.y < other.y + other.h and
            self.y + self.h > other.y
        )

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.0, PARTICLE_SPEED)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.lifetime = PARTICLE_LIFETIME
        self.size = random.randint(1, 3)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self):
        glColor3f(*self.color)
        glBegin(GL_POINTS)
        for i in range(self.size):
            for j in range(self.size):
                glVertex2f(self.x + i, self.y + j)
        glEnd()

# Initialize collision boxes
bowl_aabb = AABB(bowl_x, bowl_y, BOWL_WIDTH, BOWL_HEIGHT)
restart_button_aabb = AABB(restart_button_x, restart_button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
pause_button_aabb = AABB(pause_button_x, pause_button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
exit_button_aabb = AABB(exit_button_x, exit_button_y, BUTTON_WIDTH, BUTTON_HEIGHT)

def draw_midpoint_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    x = x1
    y = y1

    glVertex2f(x, y)
    while x <= x2:
        x += 1
        if d < 0:
            d += 2 * dy
        else:
            d += 2 * (dy - dx)
            y += 1
        glVertex2f(x, y)

def draw_arc(center_x, center_y, radius, start_angle, end_angle):
    num_segments = 100
    angle_step = (end_angle - start_angle) / num_segments
    glBegin(GL_POINTS)
    for i in range(num_segments + 1):
        angle = math.radians(start_angle + i * angle_step)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        glVertex2f(x, y)
    glEnd()

def create_explosion(x, y, color):
    for _ in range(PARTICLE_COUNT):
        particles.append(Particle(x, y, color))

def update_particles():
    global particles
    particles = [p for p in particles if p.update()]

def draw_particles():
    for particle in particles:
        particle.draw()

def update_time_slowdown():
    global time_slowdown_active, time_slowdown_timer, current_time_factor
    if time_slowdown_active:
        time_slowdown_timer -= 1
        if time_slowdown_timer <= 0:
            time_slowdown_active = False
            current_time_factor = 1.0

def egg(x, y, radius, color=YELLOW):
    glBegin(GL_POINTS)
    glColor3f(*color)
    for i in range(360):
        angle = math.radians(i)
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        glVertex2f(px, py)
    glEnd()

def draw_bomb(x, y):
    egg(x, y, BOMB_SIZE, RED)

def update_level():
    global current_level
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if points >= threshold:
            current_level = i + 1
        else:
            break

def spawn_bomb():
    if len(bombs) < (current_level + 1) and random.random() < BOMB_SPAWN_RATES[current_level]:
        x = random.uniform(BOMB_SIZE, SCREEN_WIDTH - BOMB_SIZE)
        bombs.append([x, SCREEN_HEIGHT])

def diamond_start():
    return random.uniform(DIAMOND_SIZE, SCREEN_WIDTH - DIAMOND_SIZE), SCREEN_HEIGHT

def diamond(x, y):
    egg(x, y, DIAMOND_SIZE)

def draw_rounded_rectangle(x, y, width, height, radius):
    glBegin(GL_POINTS)
    # Draw horizontal lines
    for i in range(int(x + radius), int(x + width - radius)):
        glVertex2f(i, y)
        glVertex2f(i, y + height)
    
    # Draw vertical lines
    for i in range(int(y + radius), int(y + height - radius)):
        glVertex2f(x, i)
        glVertex2f(x + width, i)
    
    # Draw corners
    for angle in range(90):
        rad = math.radians(angle)
        # Top-right corner
        glVertex2f(x + width - radius + radius * math.cos(rad),
                  y + height - radius + radius * math.sin(rad))
        # Top-left corner
        glVertex2f(x + radius - radius * math.cos(rad),
                  y + height - radius + radius * math.sin(rad))
        # Bottom-right corner
        glVertex2f(x + width - radius + radius * math.cos(rad),
                  y + radius - radius * math.sin(rad))
        # Bottom-left corner
        glVertex2f(x + radius - radius * math.cos(rad),
                  y + radius - radius * math.sin(rad))
    glEnd()

def draw_bowl():
    global bowl_x, bowl_y
    glColor3f(*RED)
    draw_rounded_rectangle(bowl_x, bowl_y, BOWL_WIDTH, BOWL_HEIGHT, 10)

def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_buttons():
    # Draw restart button
    glColor3f(*TEAL)
    draw_rounded_rectangle(restart_button_x, restart_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 5)
    glColor3f(*WHITE)
    draw_text(restart_button_x + 10, restart_button_y + 15, "R")

    # Draw pause button
    glColor3f(*AMBER)
    draw_rounded_rectangle(pause_button_x, pause_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 5)
    glColor3f(*WHITE)
    draw_text(pause_button_x + 20, pause_button_y + 15, "P")

    # Draw exit button
    glColor3f(*RED)
    draw_rounded_rectangle(exit_button_x, exit_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, 5)
    glColor3f(*WHITE)
    draw_text(exit_button_x + 20, exit_button_y + 15, "X")

def check_collision():
    global bowl_aabb, diamonds, bombs, diamonds_caught, missed_diamonds, points
    global game_over, lives, ground_diamonds, consecutive_catches
    global time_slowdown_active, time_slowdown_timer, current_time_factor

    bowl_aabb.x = bowl_x
    bowl_aabb.y = bowl_y

    for i in range(len(diamonds)-1, -1, -1):
        diamond_aabb = AABB(diamonds[i][0], diamonds[i][1], DIAMOND_SIZE, DIAMOND_SIZE)
        if diamonds[i][1] < 0:
            ground_diamonds += 1
            create_explosion(diamonds[i][0], 0, RED)
            diamonds.pop(i)
            consecutive_catches = 0
            if ground_diamonds >= DIAMONDS_PER_LIFE:
                ground_diamonds = 0
                lives -= 1
                if lives <= 0:
                    game_over = True
        elif bowl_aabb.collides_with(diamond_aabb):
            diamonds_caught += 1
            points += 10
            create_explosion(diamonds[i][0], diamonds[i][1], YELLOW)
            diamonds.pop(i)
            consecutive_catches += 1
            
            if consecutive_catches >= TIME_SLOWDOWN_THRESHOLD:
                time_slowdown_active = True
                time_slowdown_timer = TIME_SLOWDOWN_DURATION
                current_time_factor = TIME_SLOWDOWN_FACTOR
                consecutive_catches = 0
            
            update_level()

    for i in range(len(bombs)-1, -1, -1):
        bomb_aabb = AABB(bombs[i][0], bombs[i][1], BOMB_SIZE, BOMB_SIZE)
        if bombs[i][1] < 0:
            create_explosion(bombs[i][0], 0, RED)
            bombs.pop(i)
        elif bowl_aabb.collides_with(bomb_aabb):
            create_explosion(bombs[i][0], bombs[i][1], RED)
            lives -= 1
            bombs.pop(i)
            consecutive_catches = 0
            if lives <= 0:
                game_over = True

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    for diamond_x, diamond_y in diamonds:
        diamond(diamond_x, diamond_y)
    
    for bomb_x, bomb_y in bombs:
        draw_bomb(bomb_x, bomb_y)
    
    draw_bowl()
    draw_buttons()
    draw_particles()
    check_collision()
    
    glColor3f(*WHITE)
    draw_text(10, SCREEN_HEIGHT - 130, f"Lives: {lives}")
    draw_text(10, SCREEN_HEIGHT - 150, f"Points: {points}")
    draw_text(10, SCREEN_HEIGHT - 170, f"Level: {current_level + 1}")
    
    if time_slowdown_active:
        glColor3f(*TEAL)
        draw_text(10, SCREEN_HEIGHT - 210, "TIME SLOW ACTIVE!")
    else:
        glColor3f(*WHITE)
        draw_text(10, SCREEN_HEIGHT - 210, f"Catches to Slow: {TIME_SLOWDOWN_THRESHOLD - consecutive_catches}")
    
    if game_over:
        glColor3f(*RED)
        draw_text(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2, "Game Over")
    
    if current_level < len(LEVEL_THRESHOLDS):
        points_needed = LEVEL_THRESHOLDS[current_level] - points
        glColor3f(*GREEN)
        draw_text(10, SCREEN_HEIGHT - 190, f"Next level in: {points_needed} points")
    
    glutSwapBuffers()

def update(value):
    global diamonds_caught, missed_diamonds, points, game_paused

    if not game_paused and not game_over:
        update_particles()
        update_time_slowdown()
        
        if len(diamonds) < 1:
            diamonds.append(diamond_start())
        
        spawn_bomb()

        diamond_speed = DIAMOND_FALL_SPEEDS[current_level] * current_time_factor
        bomb_speed = BOMB_FALL_SPEEDS[current_level] * current_time_factor

        for i in range(len(diamonds)):
            diamonds[i] = (diamonds[i][0], diamonds[i][1] - diamond_speed)

        for i in range(len(bombs)):
            bombs[i] = [bombs[i][0], bombs[i][1] - bomb_speed]

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def special_callback(key, x, y):
    global bowl_x
    
    if game_over:
        return
        
    if key == GLUT_KEY_LEFT:
        bowl_x -= BOWL_SPEED
    elif key == GLUT_KEY_RIGHT:
        bowl_x += BOWL_SPEED
    
    bowl_x = max(0, min(SCREEN_WIDTH - BOWL_WIDTH, bowl_x))

def reset_game():
    global diamonds_caught, missed_diamonds, points, diamonds, bombs, game_paused
    global game_over, lives, ground_diamonds, current_level, particles
    global consecutive_catches, time_slowdown_active, time_slowdown_timer
    global current_time_factor
    
    diamonds_caught = 0
    missed_diamonds = 0
    points = 0
    diamonds.clear()
    bombs.clear()
    particles.clear()
    game_paused = False
    game_over = False
    lives = LIVES
    ground_diamonds = 0
    current_level = 0
    consecutive_catches = 0
    time_slowdown_active = False
    time_slowdown_timer = 0
    current_time_factor = 1.0

def mouse_callback(button, state, x, y):
    global game_paused
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if restart_button_aabb.collides_with(AABB(x, SCREEN_HEIGHT - y, 0, 0)):
            reset_game()
        elif pause_button_aabb.collides_with(AABB(x, SCREEN_HEIGHT - y, 0, 0)):
            game_paused = not game_paused
        elif exit_button_aabb.collides_with(AABB(x, SCREEN_HEIGHT - y, 0, 0)):
            glutLeaveMainLoop()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutCreateWindow(b"Diamond Catching Game")
    
    init()
    
    glutDisplayFunc(display)
    glutMouseFunc(mouse_callback)
    glutSpecialFunc(special_callback)
    glutTimerFunc(16, update, 0)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
