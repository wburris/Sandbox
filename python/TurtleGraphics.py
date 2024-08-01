import pygame
import math

class TurtleGraphics:
    def __init__(self, surface, color='green'):
        self.surface = surface
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.direction = 0
        self.position = self.center()
        self.thickness = 1
        self.penColor = color

    def turtleReset(self):
        self.position = self.center()
        self.direction = 0

    def lineThickness(self, thickness):
        self.thickness = thickness

    def lineTo(self, x, y):
        # change positive y to point up
        xstart = self.position[0]
        ystart = self.height - self.position[1]
        yend = self.height - y
        pygame.draw.line(self.surface, self.penColor, (xstart, ystart), (x, yend), self.thickness)
        self.position = (x, y)
    
    def moveTo(self, x, y):
        self.position = (x, y)

    def turnTo(self, angle):
        self.direction = angle

    def turn(self, angle):
        self.direction += angle

    def forward(self, distance, visible=True):
        x = self.position[0] + distance * math.cos(math.radians(self.direction))
        y = self.position[1] + distance * math.sin(math.radians(self.direction))
        if visible:
            self.lineTo(x, y)
        else:
            self.moveTo(x, y)
    
    def center(self):
        return (self.width / 2, self.height / 2)
    
    def setColor(self, color):
        self.penColor = color

    def pos(self):
        return self.position
    
    def size(self):
        return (self.width, self.height)
