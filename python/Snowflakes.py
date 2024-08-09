import pygame
import math
from enum import Enum
from typing import Tuple
import os
from datetime import datetime
import Control

class ControlPanel:
    def __init__(self, x, y, w, h):
        global radius
        self.rect = pygame.Rect(x, y, w, h)

        self.radiusSpinBox = Control.Spinbox(120, 40, 70, 30, 10, 300, radius, 10, self.radius_spinbox_changed)
        self.radiusLabel = Control.Label(5, 40, 70, 30, "radius:")
        self.sidesSpinBox = Control.Spinbox(120, 80, 70, 30, 1, 50, 3, 1, self.sides_spinbox_changed)
        self.sidesLabel = Control.Label(5, 80, 70, 30, "sides:")
        self.polyButton = Control.Button(10, 120, 180, 30, "Draw Polygon", self.polygon_button_clicked)
        self.reverseCheck = Control.CheckBox(10, 160, 20, 20, "Reverse Vertices", True, self.reverse_checkbox_changed)
        self.levelSpinBox = Control.Spinbox(120, 200, 70, 30, 0, 6, 3, 1, self.level_spinbox_changed)
        self.levelLabel = Control.Label(5, 200, 70, 30, "level(1-6):")
        self.kochButton = Control.Button(10, 240, 180, 30, "Koch Snowflake", self.koch_button_clicked)
        self.gosperSnowflakeButton = Control.Button(10, 280, 180, 30, "Gosper Snowflake", self.gosper_snowflake_button_clicked)
        self.squareFlakeButton = Control.Button(10, 320, 180, 30, "Square Snowflake", self.square_flake_button_clicked)
        self.sevenFlakeButton = Control.Button(10, 360, 180, 30, "7 Segment", self.seven_flake_button_clicked)
        self.eightFlakeButton = Control.Button(10, 400, 180, 30, "8 Segment", self.eight_flake_button_clicked)
        self.eightteenFlakeButton = Control.Button(10, 440, 180, 30, "18 Segment", self.eighteen_flake_button_clicked)
        self.thirtytwoFlakeButton = Control.Button(10, 480, 180, 30, "32 Segment", self.thirtytwo_flake_button_clicked)
        self.fiftyFlakeButton = Control.Button(10, 520, 180, 30, "50 Segment", self.fifty_flake_button_clicked)

    def draw(self, screen):
        pygame.draw.rect(screen, 'lightblue', self.rect)
        self.radiusSpinBox.draw(screen)
        self.radiusLabel.draw(screen)
        self.sidesSpinBox.draw(screen)
        self.sidesLabel.draw(screen)
        self.polyButton.draw(screen)
        self.reverseCheck.draw(screen)
        self.kochButton.draw(screen)
        self.levelSpinBox.draw(screen)
        self.levelLabel.draw(screen)
        self.squareFlakeButton.draw(screen)
        self.sevenFlakeButton.draw(screen)
        self.eightFlakeButton.draw(screen)
        self.eightteenFlakeButton.draw(screen)
        self.thirtytwoFlakeButton.draw(screen)
        self.gosperSnowflakeButton.draw(screen)
        self.fiftyFlakeButton.draw(screen)

    def handle_events(self, event):
        self.radiusSpinBox.handle_events(event)
        self.sidesSpinBox.handle_events(event)
        self.reverseCheck.handle_events(event)
        self.levelSpinBox.handle_events(event)

    def radius_spinbox_changed(self, value):
        global radius
        radius = value
    
    def sides_spinbox_changed(self, value):
        global num_sides
        num_sides = value

    def polygon_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.POLYGON
    
    def reverse_checkbox_changed(self, value):
        global reverse
        reverse = value

    def koch_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.KOCH

    def level_spinbox_changed(self, value):
        global level
        level = value
    
    def square_flake_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.SQUARE_FLAKE
        
    def seven_flake_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.SEVEN_SEGMENT
    
    def eight_flake_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.EIGHT_SEGMENT
    
    def eighteen_flake_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.EIGHTEEN_SEGMENT

    def thirtytwo_flake_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.THIRTYTWO_SEGMENT
    
    def fifty_flake_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.FIFTY_SEGMENT

    def gosper_snowflake_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.GOSPER_SNOWFLAKE

Point = Tuple[float, float]

class SnowFlake:
    def __init__(self, initiator, generator, dist_factor):
        self.initiator = initiator # a list of lines
        self.generator = generator # a list of angles
        self.dist_factor = dist_factor
        
    def draw(self, canvas, level):
        [self.draw_side(canvas, level, line) for line in self.initiator]
    
    def draw_side(self, canvas, level, line: Tuple[Point, Point]):
        pt1, pt2 = line
        if level == 0:
            pygame.draw.line(canvas, 'green', pt1, pt2, 2)
        else:
            angle = math.atan2(pt2[1] - pt1[1], pt2[0] - pt1[0])
            length = math.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)
            length /= self.dist_factor
            x1, y1 = pt1
            theta = 0
            for gen_angle in self.generator:
                theta += gen_angle * math.pi / 180
                current_angle = angle + theta
                x2 = x1 + length * math.cos(current_angle)
                y2 = y1 + length * math.sin(current_angle)
                pt1, pt2 = (x1,y1), (x2, y2)
                self.draw_side(canvas, level-1, (pt1, pt2))
                x1, y1 = x2, y2

def calculate_vertices(num_sides, radius, center_x, center_y, start_angle=0.0):
    vertices = []
    for n in range(num_sides):
        angle = 2 * math.pi * n / num_sides + start_angle
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices #[::-1]

def vertices_to_sides(vertices):
    return list(zip(vertices, vertices[1:] + vertices[:1]))

class DrawingMode(Enum):
    NONE = 0
    POLYGON = 1
    KOCH = 2
    SQUARE_FLAKE = 3
    SEVEN_SEGMENT = 4
    EIGHT_SEGMENT = 5
    EIGHTEEN_SEGMENT = 6
    THIRTYTWO_SEGMENT = 7
    FIFTY_SEGMENT = 8
    GOSPER_SNOWFLAKE = 9

drawing_mode = DrawingMode.NONE
level = 3
radius = 250
num_sides = 3
reverse = True

def update(canvas):
    global drawing_mode, level, radius, num_sides, angle

    canvas.fill('black')
    cx, cy = canvas.get_rect().center

    initiator = []
    if num_sides > 2:
        start_angle = math.pi / 2 - math.pi / num_sides # keep flat side down
        vertices = calculate_vertices(num_sides, radius, cx, cy, start_angle) # regular polygon
        if reverse:
            vertices = vertices[::-1]
        initiator = vertices_to_sides(vertices)
    elif num_sides == 2:
        initiator = [((cx - radius, cy - radius), (cx + radius, cy - radius)),
                     ((cx + radius, cy + radius), (cx - radius, cy + radius))] # 2 lines
    elif num_sides == 1:
        initiator = [((cx + radius, cy), (cx - radius, cy))] # line
    
    if drawing_mode == DrawingMode.POLYGON:
        if num_sides > 2:
            pygame.draw.polygon(canvas, 'green', vertices, 2)
        else:
            for line in initiator:
                pygame.draw.line(canvas, 'green', line[0], line[1], 2)   
    else:
        gen_angles = []
        if drawing_mode == DrawingMode.KOCH:
            dist_factor = 3
            gen_angles = [0, 60, -120, 60]
        elif drawing_mode == DrawingMode.SQUARE_FLAKE:
            dist_factor = math.sqrt(5)
            gen_angles = [26.5, -90, 90]
        elif drawing_mode == DrawingMode.SEVEN_SEGMENT:
            dist_factor = 3
            gen_angles = [0, -60, -60, 120, 60, 60, -120]
        elif drawing_mode == DrawingMode.GOSPER_SNOWFLAKE:
            dist_factor = math.sqrt(7)
            gen_angles = [19.12, -60, 60]
        elif drawing_mode == DrawingMode.EIGHT_SEGMENT:
            dist_factor = 4
            gen_angles = [0, -90, 90, 90, 0, -90, -90, 90]
        elif drawing_mode == DrawingMode.EIGHTEEN_SEGMENT:
            dist_factor = 6
            gen_angles = [0, -90, 0, 90, 0, 90, 90, -90, -90, 0, 90, 90, -90, -90, 0, -90, 0, 90]
        elif drawing_mode == DrawingMode.THIRTYTWO_SEGMENT:
            dist_factor = 8
            gen_angles = [-90, 90, -90, -90, 90, 90, 0, -90, 90, 90, 0, 90, -90, -90, 0, 90,
                        0, -90, 0, 90, 90, -90, 0, -90, -90, 90, 0, -90, -90, 90, 90, -90]
        elif drawing_mode == DrawingMode.FIFTY_SEGMENT:
            dist_factor = 10
            gen_angles = [0, -90, 90, 90, 0, 0, -90, 0, 90, 0,
                        -90, -90, 0, 0, -90, 0, 90, 0, 0, 0,
                        90, 90, 0, 0, -90, 0, 90, 0, 0, -90,
                        -90, 0, 0, 0, -90, 0, 90, 0, 0, 90,
                        90, 0, -90, 0, 90, 0, 0, -90, -90, 90]
        else:
            return

        snowflake = SnowFlake(initiator, gen_angles, dist_factor)
        snowflake.draw(canvas, level)

def save_screen(screen):
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    
    current_time = datetime.now()
    time_str = current_time.strftime("%Y%m%d%H%M%S")
    filename = f"screenshots/sf_{time_str}.png"
    pygame.image.save(screen, filename)

def main():
    global drawing_mode, level, radius, num_sides, angle
    pygame.init()
    #width, height = 800, 600
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Snowflakes")
    clock = pygame.time.Clock()

    border_width = 5
    cp_width, cp_height = 200, height - 2 * border_width
    cp = ControlPanel(border_width, border_width, cp_width, cp_height)

    canvas_width, canvas_height = width - cp_width - 3 * border_width, height - 2 * border_width
    canvas = pygame.Surface((canvas_width, canvas_height))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_screen(screen)
                if event.key == pygame.K_d:
                    save_screen(canvas)
            cp.handle_events(event)

        screen.fill('gray')

        cp.draw(screen)

        update(canvas)

        screen.blit(canvas, (cp_width + 2 * border_width, border_width))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
