import pygame
import math
import random
import os
from datetime import datetime
import Control

class ControlPanel:
    def __init__(self, x, y, w, h, callback=None):
        self.callback = callback
        self.rect = pygame.Rect(x, y, w, h)

        self.treeLevelSpinBox = Control.Spinbox(120, 40, 70, 30, 1, 15, 3, 1, self.tree_level_spinbox_changed)
        self.treeLevelLabel = Control.Label(5, 40, 70, 30, "tree level:")
        self.treeSizeSpinBox = Control.Spinbox(120, 80, 70, 30, 100, 600, 600, 10, self.tree_size_spinbox_changed)
        self.treeSizeLabel = Control.Label(5, 80, 70, 30, "tree size:")
        self.angleSpinBox = Control.Spinbox(120, 120, 70, 30, 10, 180, 30, 10, self.angle_spinbox_changed)
        self.angleLabel = Control.Label(5, 120, 70, 30, "angle:")

        self.random_checkbox = Control.CheckBox(20, 170, 100, 30, "random", False, self.random_checkbox_changed)
        self.bendy_checkbox = Control.CheckBox(20, 210, 100, 30, "bendy", False, self.bendy_checkbox_changed)
        self.taper_checkbox = Control.CheckBox(20, 250, 100, 30, "tapered", False, self.taper_checkbox_changed)
        self.multiple_checkbox = Control.CheckBox(20, 290, 100, 30, "multi branch", False, self.multiple_checkbox_changed)
        self.brown_checkbox = Control.CheckBox(20, 330, 100, 30, "brown", False, self.brown_checkbox_changed)


    def draw(self, screen):
        pygame.draw.rect(screen, 'lightblue', self.rect)
 
        self.treeLevelSpinBox.draw(screen)
        self.treeLevelLabel.draw(screen)
        self.treeSizeSpinBox.draw(screen)
        self.treeSizeLabel.draw(screen)
        self.angleSpinBox.draw(screen)
        self.angleLabel.draw(screen)
        self.random_checkbox.draw(screen)
        self.bendy_checkbox.draw(screen)
        self.taper_checkbox.draw(screen)
        self.multiple_checkbox.draw(screen)
        self.brown_checkbox.draw(screen)

    def handle_events(self, event):
        self.treeLevelSpinBox.handle_events(event)
        self.treeSizeSpinBox.handle_events(event)
        self.angleSpinBox.handle_events(event)
        self.random_checkbox.handle_events(event)
        self.bendy_checkbox.handle_events(event)
        self.taper_checkbox.handle_events(event)
        self.multiple_checkbox.handle_events(event)
        self.brown_checkbox.handle_events(event)
    
    def tree_level_spinbox_changed(self, value):
        global tree_level
        tree_level = value
        if self.callback is not None:
            self.callback()
    
    def tree_size_spinbox_changed(self, value):
        global tree_size
        tree_size = value
        if self.callback is not None:
            self.callback()
    
    def angle_spinbox_changed(self, value):
        global angle
        angle = value * math.pi / 180
        if self.callback is not None:
            self.callback()
    
    def random_checkbox_changed(self, value):
        global random_angle
        random_angle = value
        if self.callback is not None:
            self.callback()

    def bendy_checkbox_changed(self, value):
        global bendy_branches
        bendy_branches = value
        if self.callback is not None:
            self.callback()

    def taper_checkbox_changed(self, value):
        global tapered_tree
        tapered_tree = value
        if self.callback is not None:
            self.callback()
    
    def multiple_checkbox_changed(self, value):
        global multiple_branches
        multiple_branches = value
        if self.callback is not None:
            self.callback()
    
    def brown_checkbox_changed(self, value):
        global brown_branches
        brown_branches = value
        if self.callback is not None:
            self.callback()

class Tree:
    def __init__(self, surface):
        self.surface = surface
        self.length_scale = 0.75
        self.dtheta = math.pi / 5 # 36 degrees
        #self.max_level = 0

    def draw_branch(self, level, x, y, length, angle):
        global tapered_tree, bendy_branches, brown_branches, multiple_branches
        if level == 0:
            return
        
        jitter_angle = 20 * math.pi / 180

        height = self.surface.get_height()

        if tapered_tree:
            thickness = int(1 + (level * 0.5))
        else:
            thickness = 2

        if brown_branches and level > 3:
            branch_color = 'brown'
        else:
            branch_color = 'green'

        if bendy_branches:
            # Break the branch into three segments
            segment_length = length / 3
            mid1_x = x + (segment_length * math.cos(angle))
            mid1_y = y - (segment_length * math.sin(angle))
            
            mid2_angle = angle + random.uniform(-0.2, 0.2)  # Slight bend in the middle
            mid2_x = mid1_x + (segment_length * math.cos(mid2_angle))
            mid2_y = mid1_y - (segment_length * math.sin(mid2_angle))
            
            end_x = mid2_x + (segment_length * math.cos(angle))
            end_y = mid2_y - (segment_length * math.sin(angle))

            # Draw the three segments
            pygame.draw.line(self.surface, branch_color, (x, height - y), (mid1_x, height - mid1_y), thickness)
            pygame.draw.line(self.surface, branch_color, (mid1_x, height - mid1_y), (mid2_x, height - mid2_y), thickness)
            pygame.draw.line(self.surface, branch_color, (mid2_x, height - mid2_y), (end_x, height - end_y), thickness)
        else:
            # Calculate the end point of the branch
            end_x = x + (length * math.cos(angle))
            end_y = y - (length * math.sin(angle))
            
            # Draw the straight branch
            pygame.draw.line(self.surface, branch_color, (x, height - y), (end_x, height - end_y), thickness)

        new_length = length * self.length_scale
        if multiple_branches:
            branch_angles = [-self.dtheta, 0, self.dtheta]
        else:
            branch_angles = [-self.dtheta, self.dtheta]
        for theta in branch_angles:
            if random_angle:
                jitter = random.uniform(-jitter_angle, jitter_angle)
            else:
                jitter = 0
            self.draw_branch(level - 1, end_x, end_y, new_length, angle + theta + jitter)

    def draw(self, x, y, size, dtheta, level):
        self.dtheta = dtheta
        self.max_level = level

        level_scale = math.pow(self.length_scale, level+1)
        remaining_length = 1 - level_scale
        total_remaining_length = 1 - self.length_scale
        level_proportion = remaining_length / total_remaining_length
        start_length = size / level_proportion

        self.draw_branch(level, x, y, start_length, -math.pi/2)

def save_screen(screen):
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    
    current_time = datetime.now()
    time_str = current_time.strftime("%Y%m%d%H%M%S")
    filename = f"screenshots/tree_{time_str}.png"
    pygame.image.save(screen, filename)

tree_level = 3
tree_size = 600
angle = math.pi / 6 # 30 degrees
random_angle = False
bendy_branches = False
tapered_tree = False
multiple_branches = False
brown_branches = False
surface_width, surface_height = 100, 100
pygame_surface = None

def draw_tree():
    global pygame_surface, tree_level, tree_size, angle
    global random_angle, bendy_branches, tapered_tree, multiple_branches
    
    if pygame_surface is None:
        pygame_surface = pygame.Surface((surface_width, surface_height))
    pygame_surface.fill('black')
    width = pygame_surface.get_width()
    x = width //2
    y = 100
    tree = Tree(pygame_surface)
    tree.draw(x, y, tree_size, angle, tree_level)

def main():
    global tree_level, tree_size, angle, random_angle, bendy_branches, tapered_tree, multiple_branches
    global pygame_surface, surface_width, surface_height
    pygame.init()
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Trees")
    clock = pygame.time.Clock()

    border_width = 5
    control_panel_width = 200
    surface_width = width - control_panel_width - 3 * border_width
    surface_height = height - 2 * border_width

    cp = ControlPanel(border_width, border_width, control_panel_width, height - border_width, draw_tree)
    draw_tree()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_screen(screen)
            cp.handle_events(event)

        screen.fill('gray')

        cp.draw(screen)

        if pygame_surface is not None:
            screen.blit(pygame_surface, (control_panel_width + 2 * border_width, 5))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
