import pygame
import math
from enum import Enum
from typing import List, Tuple
import os
from datetime import datetime
import Control
import TurtleGraphics

class ControlPanel:
    def __init__(self, x, y, w, h):
        global radius
        self.rect = pygame.Rect(x, y, w, h)

        self.radiusSpinBox = Control.Spinbox(120, 40, 70, 30, 10, 300, radius, 10, self.radius_spinbox_changed)
        self.radiusLabel = Control.Label(5, 40, 70, 30, "radius:")
        self.sidesSpinBox = Control.Spinbox(120, 80, 70, 30, 3, 50, 3, 1, self.sides_spinbox_changed)
        self.sidesLabel = Control.Label(5, 80, 70, 30, "sides:")
        self.polyButton = Control.Button(10, 120, 180, 30, "Draw Polygon", self.polygon_button_clicked)
        self.levelSpinBox = Control.Spinbox(120, 200, 70, 30, 0, 6, 3, 1, self.level_spinbox_changed)
        self.levelLabel = Control.Label(5, 200, 70, 30, "level(1-6):")
        self.angleSpinBox = Control.Spinbox(120, 240, 70, 30, 0, 89, 60, 1, self.angle_spinbox_changed)
        self.angleLabel = Control.Label(5, 240, 70, 30, "angle:")
        self.kochButton = Control.Button(10, 280, 180, 30, "Koch Snowflake", self.koch_button_clicked)
        self.gosperSnowflakeButton = Control.Button(10, 320, 180, 30, "Gosper Snowflake", self.gosper_snowflake_button_clicked)
        self.gosperButton = Control.Button(10, 400, 180, 30, "Gosper Curve", self.gosper_button_clicked)
        self.tileGosperButton = Control.Button(10, 440, 180, 30, "Tile Gosper", self.tile_gosper_button_clicked)

    def draw(self, screen):
        pygame.draw.rect(screen, 'lightblue', self.rect)
        self.radiusSpinBox.draw(screen)
        self.radiusLabel.draw(screen)
        self.sidesSpinBox.draw(screen)
        self.sidesLabel.draw(screen)
        self.polyButton.draw(screen)
        self.kochButton.draw(screen)
        self.levelSpinBox.draw(screen)
        self.levelLabel.draw(screen)
        self.angleSpinBox.draw(screen)
        self.angleLabel.draw(screen)
        self.gosperSnowflakeButton.draw(screen)
        self.gosperButton.draw(screen)
        self.tileGosperButton.draw(screen)

    def handle_events(self, event):
        self.radiusSpinBox.handle_events(event)
        self.sidesSpinBox.handle_events(event)
        self.levelSpinBox.handle_events(event)
        self.angleSpinBox.handle_events(event)

    def radius_spinbox_changed(self, value):
        global radius
        radius = value
    
    def sides_spinbox_changed(self, value):
        global num_sides
        num_sides = value

    def polygon_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.POLYGON

    def koch_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.KOCH

    def level_spinbox_changed(self, value):
        global level
        level = value
    
    def angle_spinbox_changed(self, value):
        global angle
        angle = value

    def gosper_snowflake_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.GOSPER_SNOWFLAKE

    def gosper_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.GOSPER
    
    def tile_gosper_button_clicked(self):
        global drawing_mode
        drawing_mode = DrawingMode.TILE_GOSPER

Point = Tuple[float, float]

class Koch:
    def __init__(self, vertices, angle_degrees=60):
        self.vertices = vertices
        self.angle_rad = math.radians(angle_degrees)
        self.cos_angle = math.cos(self.angle_rad)
        self.sin_angle = math.sin(self.angle_rad)
        self.dist_factor = 1 / (2 * (1 + self.cos_angle))
        #self.dist_factor = 1 / 3

    def draw(self, surface, level):
        sides = list(zip(self.vertices, self.vertices[1:] + self.vertices[:1])) # List[Tuple[Point, Point]]
        [self.draw_side(surface, level, side) for side in sides]

    def draw_side(self, surface, level, side: Tuple[Point, Point]):
        pt1, pt2 = side
        if level == 0:
            pygame.draw.line(surface, 'green', pt1, pt2, 2)
        else:
            pt3, pt4, pt5 = self._calculate_triangle_points(pt1, pt2) # form a triangle

            for new_side in [(pt1, pt3), (pt3, pt5), (pt5, pt4), (pt4, pt2)]:
                self.draw_side(surface, level - 1, new_side)

    def _calculate_triangle_points(self, pt1: Point, pt2: Point) -> Tuple[Point, Point, Point]:
        x1, y1 = pt1
        x2, y2 = pt2

        # calculate pt3 and pt4 using weighted average
        w = self.dist_factor
        pt3 = ((1 - w) * x1 + w * x2, (1 - w) * y1 + w * y2)
        pt4 = (w * x1 + (1 - w) * x2, w * y1 + (1 - w) * y2)

        dx, dy = pt4[0] - pt3[0], pt4[1] - pt3[1] # vector from pt3 to pt4

        distance = math.sqrt(dx ** 2 + dy ** 2) # distance from pt3 to pt4
        xm, ym = (pt3[0] + pt4[0]) / 2, (pt3[1] + pt4[1]) / 2 # midpoint of pt3 and pt4
        h = distance / 2 * math.tan(self.angle_rad) # height of the triangle
        dx_norm, dy_norm = dx / distance, dy / distance # normalize the vector
        px, py = -dy_norm, dx_norm # perpendicular vector

        # find the peak of the triangle
        pt5 = ( xm + h * px, ym + h * py)

        return pt3, pt4, pt5

class GosperCurve:
    def __init__(self, turtle):
        self.turtle = turtle
        self.endpoints = []

    def draw_gosper_generator(self, order, size):
        if order == 0:
            self.turtle.forward(size)
        else:
            self.draw_gosper_generator(order-1, size)
            self.turtle.turn(60)
            self.draw_gosper_generator(order-1, size)
            self.turtle.turn(-60)
            self.draw_gosper_generator(order-1, size)

    def gosper_curve(self, order, size, save_endpoints=False):
        for _ in range(6):
            if save_endpoints:
                self.endpoints.append(self.turtle.pos())
            self.draw_gosper_generator(order, size)
            self.turtle.turn(-60)
   
    def draw(self):
        order = 3
        size = 10
        self.turtle.lineThickness(2)
        self.turtle.forward(-150, False)
        self.gosper_curve(order, size)

    def tile(self):
        order = 3
        size = 3
        cx, cy = self.turtle.center()
        self.turtle.moveTo(50, cy + 200)
        x0, y0 = self.turtle.pos()

        self.gosper_curve(order, size, True)

        row_deltax = self.endpoints[2][0] - self.endpoints[0][0]
        row_deltay = self.endpoints[2][1] - self.endpoints[0][1]
        col_deltax = self.endpoints[4][0] - self.endpoints[0][0]
        col_deltay = self.endpoints[4][1] - self.endpoints[0][1]

        for c in range(4):
            for r in range(3):
                self.turtle.moveTo(x0+(r-c)*row_deltax+(r+c)*col_deltax, y0+(r-c)*row_deltay+(r+c)*col_deltay)
                self.gosper_curve(order, size)
                self.turtle.moveTo(x0+(r-c)*row_deltax+(r+c+1)*col_deltax, y0+(r-c)*row_deltay+(r+c+1)*col_deltay)
                self.gosper_curve(order, size)

class GosperSnowflake:
    def __init__(self, vertices):
        self.vertices = vertices
        self.dist_factor = math.sqrt(7)

    def draw(self, surface, level):
        sides = list(zip(self.vertices, self.vertices[1:] + self.vertices[:1])) # List[Tuple[Point, Point]]
        [self.draw_side(surface, level, side) for side in sides]
    
    def draw_side(self, surface, level, side: Tuple[Point, Point]):
        pt1, pt2 = side
        if level == 0:
            pygame.draw.line(surface, 'green', pt1, pt2, 2)
        else:
            angle = math.atan2(pt2[1] - pt1[1], pt2[0] - pt1[0]) * 180 / math.pi
            length = math.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)
            length /= math.sqrt(7)
            x1, y1 = pt1
            for a in [19.12, -60 + 19.12, 19.12]:
                current_angle = angle + a
                x2 = x1 + length * math.cos(current_angle * math.pi / 180)
                y2 = y1 + length * math.sin(current_angle * math.pi / 180)
                pt1, pt2 = (x1,y1), (x2, y2)
                self.draw_side(surface, level-1, (pt1, pt2))
                x1, y1 = x2, y2

def calculate_vertices(num_sides, radius, center_x, center_y):
    vertices = []
    for angle in [2 * math.pi * n / num_sides for n in range(num_sides)]:
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices[::-1]

class DrawingMode(Enum):
    NONE = 0
    POLYGON = 1
    KOCH = 2
    GOSPER_SNOWFLAKE = 3
    GOSPER = 4
    TILE_GOSPER = 5
    MULTI = 6

drawing_mode = DrawingMode.NONE
level = 3
radius = 200
num_sides = 3
angle = 60

def multi_draw(drawing_surface):
    width, height = drawing_surface.get_size()
    drawing_surface.fill('black')

    radius = min(width, height) / 4 - 20

    level = 3
    cx, cy = width / 4, height / 4
    num_sides = 3
    angle = 60
    polygon = calculate_vertices(num_sides, radius, cx, cy)
    snowflake = Koch(polygon, angle)
    snowflake.draw(drawing_surface, level)

    level = 2
    cx, cy = width - width / 4, height / 4
    num_sides = 3
    angle = 80
    polygon = calculate_vertices(num_sides, radius, cx, cy)
    snowflake = Koch(polygon, angle)
    snowflake.draw(drawing_surface, level)

    level = 3
    cx, cy = width / 4, height - height / 4
    num_sides = 4
    angle = 80
    polygon = calculate_vertices(num_sides, radius, cx, cy)
    snowflake = Koch(polygon, angle)
    snowflake.draw(drawing_surface, level)

    level = 6
    cx, cy = width - width / 4, height - height / 4
    num_sides = 3
    angle = 80
    polygon = calculate_vertices(num_sides, radius, cx, cy)
    snowflake = Koch(polygon, angle)
    snowflake.draw(drawing_surface, level)

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
    width, height = 800, 600
    #width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Snowflakes")
    clock = pygame.time.Clock()

    border_width = 5
    cp_width, cp_height = 200, height - 2 * border_width
    surface_width, surface_height = width - cp_width - 3 * border_width, height - 2 * border_width
    
    cp = ControlPanel(border_width, border_width, cp_width, cp_height)

    drawing_surface = pygame.Surface((surface_width, surface_height))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_screen(screen)
                if event.key == pygame.K_d:
                    save_screen(drawing_surface)
                if event.key == pygame.K_m:
                    drawing_mode = DrawingMode.MULTI
                    multi_draw(drawing_surface)
            cp.handle_events(event)

        screen.fill('gray')

        cp.draw(screen)

        if drawing_mode == DrawingMode.POLYGON:
            if num_sides > 2:
                cx, cy = drawing_surface.get_rect().center
                polygon = calculate_vertices(num_sides, radius, cx, cy)
                drawing_surface.fill('black')
                pygame.draw.polygon(drawing_surface, 'green', polygon, 2)
        elif drawing_mode == DrawingMode.KOCH:
            if level >= 0:
                cx, cy = drawing_surface.get_rect().center
                polygon = calculate_vertices(num_sides, radius, cx, cy)
                snowflake = Koch(polygon, angle)
                drawing_surface.fill('black')
                snowflake.draw(drawing_surface, level)
        elif drawing_mode == DrawingMode.GOSPER_SNOWFLAKE:
            if level >= 0:
                cx, cy = drawing_surface.get_rect().center
                polygon = calculate_vertices(num_sides, radius, cx, cy)
                snowflake = GosperSnowflake(polygon)
                drawing_surface.fill('black')
                snowflake.draw(drawing_surface, level)
        elif drawing_mode == DrawingMode.GOSPER:
            tg = TurtleGraphics.TurtleGraphics(drawing_surface)
            snowflake = GosperCurve(tg)
            drawing_surface.fill('black')
            snowflake.draw()
        elif drawing_mode == DrawingMode.TILE_GOSPER:
            tg = TurtleGraphics.TurtleGraphics(drawing_surface)
            snowflake = GosperCurve(tg)
            drawing_surface.fill('black')
            snowflake.tile()

        screen.blit(drawing_surface, (cp_width + 2 * border_width, border_width))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
