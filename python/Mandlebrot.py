import pygame
import numpy as np
from numba import jit
from enum import Enum
import os
from datetime import datetime
import time

@jit(nopython=True)
def mandelbrot(width, height, corner1, scaleReal, scaleImag, itsMaxIter):
    pixel_data = np.zeros((width, height), dtype=np.uint16)

    for x, y in np.ndindex(pixel_data.shape):
        c = corner1 + complex(x * scaleReal, y * scaleImag)
        col = itsMaxIter
        z = 0
        for n in range(itsMaxIter):
            if abs(z) > 2.0:
                col = n
                break
            z = z * z + c
        pixel_data[x, y] = col

    return pixel_data

@jit(nopython=True)
def julia(width, height, corner1, C, scaleReal, scaleImag, itsMaxIter):
    pixel_data = np.zeros((width, height), dtype=np.uint16)

    for x, y in np.ndindex(pixel_data.shape):
        z = corner1 + complex(x * scaleReal, y * scaleImag)
        col = itsMaxIter
        n = 0
        for n in range(itsMaxIter):
            if abs(z) > 2.0:
                col = n
                break
            z = z * z + C
        pixel_data[x, y] = col

    return pixel_data

palette = None
color_data = None
pygame_surface = None
preview_surface = None
preview_enabled = False

class DrawingMode(Enum):
    NONE = 0
    MANDELBROT = 1
    JULIA = 2

class Fractals:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.mouseDown = False
        self.dragStart = (0, 0)
        self.corner1 = complex(-2.25, -1.5)
        self.corner2 = complex(0.75, 1.5)
        self.center = complex(-0.75, 0.0)

        self.maxIterations = 1024

        self.scale = 3 / min(width, height)

        self.drawing_mode = DrawingMode.MANDELBROT

        self.julia_C = complex(0.285, 0.01)

        self.mouse_pos = (0, 0)
        self.last_zoom_time = 0
        self.min_selection_size = 5

    def max_iterations(self):
        return self.maxIterations
    
    def UpdateCorners(self):
        realMin = self.center.real - (self.width / 2) * self.scale
        imagMin = self.center.imag - (self.height / 2) * self.scale
        realMax = self.center.real + (self.width / 2) * self.scale
        imagMax = self.center.imag + (self.height / 2) * self.scale
        self.corner1 = complex(realMin, imagMin)
        self.corner2 = complex(realMax, imagMax)

    def MoveCenter(self, offsetx, offsety):
        offsetReal = offsetx * self.scale
        offsetImag = offsety * self.scale
        self.center = self.center + complex(offsetReal, offsetImag)
        self.UpdateCorners()

    def ZoomIn(self, amount=2):
        self.scale /= amount
        self.UpdateCorners()

    def ZoomOut(self, amount=2):
        self.scale *= amount
        self.UpdateCorners()

    def zoomRect(self, rect):
        x1 = rect[0]
        y1 = rect[1]
        x2 = rect[0] + rect.width
        y2 = rect[1] + rect.height

        xcenter = self.width / 2
        ycenter = self.height / 2

        midx = (x1 + x2) / 2
        midy = (y1 + y2) / 2

        self.MoveCenter(midx - xcenter, midy - ycenter)

        xratio = self.width / (x2 - x1)
        yratio = self.height / (y2 - y1)
        scale = min(xratio, yratio)

        self.ZoomIn(scale)

        self.redraw()

    def zoomPoint(self, zoom_point):
        xCenter = self.width / 2
        yCenter = self.height / 2
        self.MoveCenter(zoom_point[0] - xCenter, zoom_point[1] - yCenter)
        self.ZoomIn()
        self.redraw()

    def draw_selection_rectangle(self, screen):
        if self.mouseDown:
            mouse_pos = pygame.mouse.get_pos()
            x = min(self.dragStart[0], mouse_pos[0])
            y = min(self.dragStart[1], mouse_pos[1])
            width = abs(mouse_pos[0] - self.dragStart[0])
            height = abs(mouse_pos[1] - self.dragStart[1])
            pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 3)

    def mouse_down(self, pos):
        current_time = time.time()
        if not self.mouseDown and current_time - self.last_zoom_time > 0.3: # 300 ms delay
            self.mouseDown = True
            self.dragStart = pos

    def mouse_up(self):
        if self.mouseDown:
            self.mouseDown = False
            mouse_pos = pygame.mouse.get_pos()
            self.dragEnd = mouse_pos
            left = min(self.dragStart[0], self.dragEnd[0])
            top = min(self.dragStart[1], self.dragEnd[1])
            width = abs(self.dragStart[0] - self.dragEnd[0])
            height = abs(self.dragStart[1] - self.dragEnd[1])
            if width > self.min_selection_size and height > self.min_selection_size:
                rect = pygame.Rect(left, top, width, height)
                self.zoomRect(rect)
            else:
                self.zoomPoint(self.dragStart)
            self.last_zoom_time = time.time()
    
    def mouse_move(self, screen):
        self.mouse_pos = pygame.mouse.get_pos()
        self.julia_preview()
            
    def mandelbrot_set(self):
        self.UpdateCorners()
        return mandelbrot(self.width, self.height, self.corner1,
                          self.scale, self.scale, self.maxIterations)
    
    def julia_set(self):
        self.UpdateCorners()
        return julia(self.width, self.height, self.corner1, self.julia_C,
                     self.scale, self.scale, self.maxIterations)

    def julia_preview(self):
        width = 256
        height = 256
        scale = 4 / max(width, height)
        mouse_pos = pygame.mouse.get_pos()
        real = self.corner1.real + (mouse_pos[0] / self.width) * (self.corner2.real - self.corner1.real)
        imag = self.corner1.imag + ((self.height - mouse_pos[1]) / self.height) * (self.corner2.imag - self.corner1.imag)
        C = complex(real, imag)
        corner = complex(-2, -2)
        return julia(width, height, corner, C, scale, scale, self.maxIterations)
    
    def redraw(self):
        global palette, color_data, pygame_surface, preview_surface
        if self.drawing_mode == DrawingMode.MANDELBROT:
            pixel_data = self.mandelbrot_set()
        elif self.drawing_mode == DrawingMode.JULIA:
            pixel_data = self.julia_set()
            preview_surface = None
        else:
            print("Drawing mode not set")
            return
        color_data = apply_palette(pixel_data, palette)
        pygame_surface = pygame.pixelcopy.make_surface(color_data)

    # page 283 of Fractal Programming in C by Roger T. Stevens
    # iterations, real, imag
    juliasets = [
        [128, 0.238498, 0.519198],  # A
        [96, -0.743036, 0.113467],  # B
        [64, -0.192175, 0.656734],  # C
        [32, 0.108294, -0.670487],  # D
        [64, -0.392488, -0.587966],  # E
        [256, -0.392488, -0.587966],  # F
        [32, 0.138341, 0.649857],  # G
        [24, 0.278560, -0.003483],  # H
        [48, -1.258842, 0.065330],  # I
        [48, -1.028482, -0.264756],  # J
        [64, 0.268545, -0.003483],  # K
        [64, 0.268545, -0.003483],  # L
        [24, 0.268545, -0.003483],  # M
        [256, 0.318623, 0.044699],  # N
        [48, 0.318623, 0.429799]  # O
    ]

    def draw_julia(self, n):
        n = abs(n)
        if n > len(self.juliasets):
            return
        pygame.display.set_caption("Julia")
        self.julia_C = complex(self.juliasets[n][1], self.juliasets[n][2])
        self.drawing_mode = DrawingMode.JULIA
        #self.maxIterations = self.juliasets[n][0]
        self.scale = 3 / min(self.width, self.height)
        self.center = complex(0, 0)
        self.UpdateCorners()

        self.redraw()

    def set_mode(self, mode):
        if self.drawing_mode == DrawingMode.MANDELBROT and mode == DrawingMode.JULIA:
            mouse_pos = pygame.mouse.get_pos()
            real = self.corner1.real + (mouse_pos[0] / self.width) * (self.corner2.real - self.corner1.real)
            imag = self.corner1.imag + ((self.height - mouse_pos[1]) / self.height) * (self.corner2.imag - self.corner1.imag)
            self.julia_C = complex(real, imag)
            self.drawing_mode = mode
            self.center = complex(0, 0)
            self.UpdateCorners()
            scale = 3 / min(self.width, self.height)
            self.scale = scale
        elif self.drawing_mode == DrawingMode.JULIA and mode == DrawingMode.MANDELBROT:
            self.drawing_mode = mode
            self.center = complex(-0.75, 0.0)
            self.UpdateCorners()
            scale = 4 / max(self.width, self.height)
            self.scale = scale
        self.redraw()

    def mode(self):
        return self.drawing_mode
    
    def update(self, screen):
        global preview_surface, preview_enabled
        if self.mouseDown:
            self.mouse_down(screen)
        if preview_enabled:
            julia_preview_pixel_data = self.julia_preview()
            julia_preview_color_data = apply_palette(julia_preview_pixel_data, palette)
            preview_surface = pygame.pixelcopy.make_surface(julia_preview_color_data)

    def save_screen(self, screen):
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        current_time = datetime.now()
        time_str = current_time.strftime("%Y%m%d%H%M%S")
        if self.drawing_mode == DrawingMode.MANDELBROT:
            filename = f"screenshots/man_{time_str}.png"
        elif self.drawing_mode == DrawingMode.JULIA:
            filename = f"screenshots/julia_{time_str}.png"
        pygame.image.save(screen, filename)

def load_palette(filename):
    palette = []
    with open(filename, 'r') as file:
        for line in file:
            r, g, b = map(int, line.split())
            palette.append((r, g, b))
    return np.array(palette, dtype=np.uint8)

def apply_palette(pixel_data, palette):
    # Find the maximum value in pixel_data
    max_value = np.max(pixel_data)

    # Calculate the scaling factor
    scaling_factor = (len(palette)-1) / max_value

    # Scale the pixel_data values to match the size of the palette
    scaled_pixel_data = (pixel_data * scaling_factor).astype(int)

    # Use the scaled values to index into the palette
    color_data = palette[scaled_pixel_data]

    return color_data

def create_palette(size):
    palette = np.zeros((size, 3), dtype=np.uint8)
    start_color_angle = 0
    range_color_angle = 360
    for i in range(size-1):
        hue = int(i / size * range_color_angle + start_color_angle)
        color = pygame.Color(0)
        color.hsla = (hue, 100, 50, 100)
        palette[i] = [color.r, color.g, color.b]
    palette[size-1] = [0, 0, 0] # black
    return palette

def create_gradient_palette(size, c1, c2):
    palette = np.zeros((size, 3), dtype=np.uint8)
    
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    r_range = np.linspace(r1, r2, size-1)
    g_range = np.linspace(g1, g2, size-1)
    b_range = np.linspace(b1, b2, size-1)
    palette[:-1] = np.stack([r_range, g_range, b_range]).T
    palette[-1] =  [0, 0, 0] # black
    
    return palette

def main():
    global palette, color_data, pygame_surface, preview_surface, preview_enabled
    pygame.init()
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Mandlebrot")
    clock = pygame.time.Clock()

    fractals = Fractals(width, height)
    pixel_data = fractals.mandelbrot_set()

    #palette = load_palette('palette.txt')
    size = fractals.max_iterations()
    palette = create_palette(size)
    #palette = create_gradient_palette(size, (0, 255, 0), (255, 0, 0))
    #palette = create_gradient_palette(size, (255,255,0), (0,0,255))

    color_data = apply_palette(pixel_data, palette)

    # Create a Pygame surface from the color data
    pygame_surface = pygame.pixelcopy.make_surface(color_data)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    fractals.mouse_down(pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    fractals.mouse_up()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_PLUS:
                    fractals.ZoomIn()
                    fractals.redraw()
                elif event.key == pygame.K_KP_MINUS:
                    fractals.ZoomOut()
                    fractals.redraw()
                elif event.key == pygame.K_s:
                    fractals.save_screen(screen)
                elif event.key == pygame.K_j:
                    fractals.set_mode(DrawingMode.JULIA)
                    pygame.display.set_caption("Julia")
                    fractals.redraw()
                elif event.key == pygame.K_m:
                    fractals.set_mode(DrawingMode.MANDELBROT)
                    pygame.display.set_caption("Mandlebrot")
                    fractals.redraw()
                elif event.key == pygame.K_p:
                    preview_enabled = not preview_enabled
                    #fractals.redraw()
                elif event.key == pygame.K_1:
                    fractals.draw_julia(0)
                elif event.key == pygame.K_2:
                    fractals.draw_julia(1)
                elif event.key == pygame.K_3:
                    fractals.draw_julia(2)
                elif event.key == pygame.K_4:
                    fractals.draw_julia(3)
                elif event.key == pygame.K_5:
                    fractals.draw_julia(4)
                elif event.key == pygame.K_6:
                    fractals.draw_julia(5)
                elif event.key == pygame.K_7:
                    fractals.draw_julia(6)
                elif event.key == pygame.K_8:
                    fractals.draw_julia(7)
                elif event.key == pygame.K_9:
                    fractals.draw_julia(8)
                elif event.key == pygame.K_0:
                    fractals.draw_julia(9)
                elif event.key == pygame.K_q:
                    fractals.draw_julia(10)
                elif event.key == pygame.K_w:
                    fractals.draw_julia(11)
                elif event.key == pygame.K_e:
                    fractals.draw_julia(12)
                elif event.key == pygame.K_r:
                    fractals.draw_julia(13)

        fractals.update(screen)

        # Draw the main fractal
        screen.blit(pygame_surface, (0, 0))

        # Draw the Julia set preview
        if preview_enabled and (preview_surface is not None) and (fractals.mode() == DrawingMode.MANDELBROT):
                screen.blit(preview_surface, (0, 0))

        # Draw the selection rectangle
        fractals.draw_selection_rectangle(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
    