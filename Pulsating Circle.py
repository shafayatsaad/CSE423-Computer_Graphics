from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Custom window dimensions ensuring minimum 512x512
WINDOW_SIZE = 512

class CircleSystem:
    def __init__(self):
        self.center_x = WINDOW_SIZE // 2
        self.center_y = WINDOW_SIZE // 2
        self.inner_r = 50
        self.outer_r = 100
        self.is_pulsing = True
        self.pulse_amount = 0
        self.pulse_increasing = True
        
    def mpl_plot_point(self, x, y):
        """Custom point plotting for Midpoint Line Algorithm"""
        glVertex2f(x, y)
    
    def mpl_draw_line(self, x1, y1, x2, y2, dashed=False):
        """Pure Midpoint Line Algorithm implementation"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steep = dy > dx
        
        # If line is steep, transpose coordinates
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
            
        # Ensure line is left to right
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            
        dx = x2 - x1
        dy = abs(y2 - y1)
        error = dx // 2
        y = y1
        y_step = 1 if y1 < y2 else -1
        dash_count = 0
        
        glBegin(GL_POINTS)
        for x in range(x1, x2 + 1):
            dash_count += 1
            if not dashed or dash_count % 10 < 5:  # Dash pattern
                if steep:
                    self.mpl_plot_point(y, x)
                else:
                    self.mpl_plot_point(x, y)
                    
            error -= dy
            if error < 0:
                y += y_step
                error += dx
        glEnd()
    
    def mpc_plot_points(self, xc, yc, x, y, outer=False):
        """Plot points for Midpoint Circle Algorithm with eight-way symmetry"""
        points = [
            (x, y), (-x, y), (x, -y), (-x, -y),
            (y, x), (-y, x), (y, -x), (-y, -x)
        ]
        
        for dx, dy in points:
            px = (xc + dx) % WINDOW_SIZE
            py = (yc + dy) % WINDOW_SIZE
            
            if outer:
                # Determine quadrant color
                if px >= WINDOW_SIZE/2:
                    if py >= WINDOW_SIZE/2:
                        glColor3f(1, 0, 0)  # Red - top right
                    else:
                        glColor3f(1, 1, 0)  # Yellow - bottom right
                else:
                    if py >= WINDOW_SIZE/2:
                        glColor3f(0, 1, 0)  # Green - top left
                    else:
                        glColor3f(0, 0, 1)  # Blue - bottom left
            
            self.mpl_plot_point(px, py)
    
    def mpc_draw_circle(self, xc, yc, radius, outer=False):
        """Pure Midpoint Circle Algorithm implementation"""
        x = 0
        y = radius
        p = 1 - radius
        
        glBegin(GL_POINTS)
        while x <= y:
            self.mpc_plot_points(xc, yc, x, y, outer)
            
            if p < 0:
                p += 2 * x + 1
            else:
                y -= 1
                p += 2 * (x - y) + 1
            x += 1
        glEnd()
    
    def draw_quadrants(self):
        """Draw quadrant divisions using MPL"""
        glColor3f(1, 1, 1)
        mid = WINDOW_SIZE // 2
        # Vertical dashed line
        self.mpl_draw_line(mid, 0, mid, WINDOW_SIZE, True)
        # Horizontal dashed line
        self.mpl_draw_line(0, mid, WINDOW_SIZE, mid, True)
    
    def update_pulse(self):
        """Handle pulsating effect"""
        if self.is_pulsing:
            if self.pulse_increasing:
                self.pulse_amount += 0.5
                if self.pulse_amount >= 20:
                    self.pulse_increasing = False
            else:
                self.pulse_amount -= 0.5
                if self.pulse_amount <= -20:
                    self.pulse_increasing = True
    
    def draw(self):
        """Main drawing function"""
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Draw quadrant divisions
        self.draw_quadrants()
        
        # Update pulsing effect
        self.update_pulse()
        
        # Draw outer pulsating circle
        outer_radius = self.outer_r + self.pulse_amount
        self.mpc_draw_circle(self.center_x, self.center_y, int(outer_radius), True)
        
        # Draw inner circle (white, constant radius)
        glColor3f(1, 1, 1)
        self.mpc_draw_circle(self.center_x, self.center_y, self.inner_r)
        
        glutSwapBuffers()
    
    def handle_keyboard(self, key, x, y):
        """Handle keyboard input"""
        if key == b' ':
            self.is_pulsing = not self.is_pulsing
        glutPostRedisplay()
    
    def handle_special(self, key, x, y):
        """Handle special keys (arrows)"""
        if key == GLUT_KEY_UP:
            self.center_y = (self.center_y + 5) % WINDOW_SIZE
        elif key == GLUT_KEY_DOWN:
            self.center_y = (self.center_y - 5) % WINDOW_SIZE
        elif key == GLUT_KEY_LEFT:
            self.center_x = (self.center_x - 5) % WINDOW_SIZE
        elif key == GLUT_KEY_RIGHT:
            self.center_x = (self.center_x + 5) % WINDOW_SIZE
        glutPostRedisplay()
    
    def handle_mouse(self, button, state, x, y):
        """Handle mouse input"""
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            self.center_x = x
            self.center_y = WINDOW_SIZE - y
            glutPostRedisplay()

def init():
    """Initialize OpenGL settings"""
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_SIZE, 0, WINDOW_SIZE)

def main():
    """Main function"""
    circles = CircleSystem()
    
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_SIZE, WINDOW_SIZE)
    glutCreateWindow(b'Circle System')
    
    init()
    
    glutDisplayFunc(lambda: circles.draw())
    glutKeyboardFunc(lambda *args: circles.handle_keyboard(*args))
    glutSpecialFunc(lambda *args: circles.handle_special(*args))
    glutMouseFunc(lambda *args: circles.handle_mouse(*args))
    glutIdleFunc(lambda: circles.draw())
    
    glutMainLoop()

if __name__ == "__main__":
    main()