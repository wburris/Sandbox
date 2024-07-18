import pygame

class Spinbox:
    def __init__(self, x, y, width, height, min_value, max_value, initial_value, step=1, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = initial_value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.callback = callback
        self.font = pygame.font.Font(None, 30)
        self.up_rect = pygame.Rect(x + width - 20, y, 20, height // 2)
        self.down_rect = pygame.Rect(x + width - 20, y + height // 2, 20, height // 2)

    def draw(self, surface):
        # Draw main rectangle
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)

        # Draw up and down buttons
        pygame.draw.rect(surface, (150, 150, 150), self.up_rect)
        pygame.draw.rect(surface, (150, 150, 150), self.down_rect)

        # Draw arrows
        pygame.draw.polygon(surface, (0, 0, 0), 
            [(self.up_rect.centerx, self.up_rect.top + 5),
             (self.up_rect.left + 5, self.up_rect.bottom - 5),
             (self.up_rect.right - 5, self.up_rect.bottom - 5)])
        pygame.draw.polygon(surface, (0, 0, 0), 
            [(self.down_rect.centerx, self.down_rect.bottom - 5),
             (self.down_rect.left + 5, self.down_rect.top + 5),
             (self.down_rect.right - 5, self.down_rect.top + 5)])

        # Draw value
        text_surface = self.font.render(str(self.value), True, (0, 0, 0))
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 6))

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.up_rect.collidepoint(event.pos):
                self.increment()
            elif self.down_rect.collidepoint(event.pos):
                self.decrement()

    def increment(self):
        self.value = min(self.value + self.step, self.max_value)
        if self.callback is not None:
            self.callback(self.value)

    def decrement(self):
        self.value = max(self.value - self.step, self.min_value)
        if self.callback is not None:
            self.callback(self.value)

class Label:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 30)

    def draw(self, surface):
        label_surface = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(label_surface, (self.rect.x + 10, self.rect.y + 6))

class CheckBox:
    def __init__(self, x, y, width, height, text, checked=False, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        #self.check_rect = pygame.Rect(x + width - 15, y + 8, 15, 15)
        self.check_rect = pygame.Rect(x, y, 20, 20)
        self.text = text
        self.checked = checked
        self.callback = callback
        self.font = pygame.font.Font(None, 30)

    def draw(self, surface):
        # Draw the checkbox
        if self.checked:
            pygame.draw.rect(surface, (0, 0, 0), self.check_rect)
        else:
            pygame.draw.rect(surface, (200, 200, 200), self.check_rect)
        pygame.draw.rect(surface, (100, 100, 100), self.check_rect, 2)

        label_surface = self.font.render(self.text, True, (0, 0, 0))

        # Position the text next to the checkbox
        text_x = self.check_rect.right + 10  # 10 pixels of padding
        text_y = self.check_rect.centery - label_surface.get_height() // 2  # Vertically center the text

        surface.blit(label_surface, (text_x, text_y))
    
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.callback is not None:
                    self.callback(self.checked)

class Button():
    def __init__(self, x, y, w, h, label, callback):
        self.rect = (x, y, w, h)
        self.label = label
        self.clicked = False
        self.font = pygame.font.SysFont('Arial', 20)
        self.callback = callback
 
    def draw(self, surface):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        button_rect = pygame.rect.Rect(self.rect)
    
        if button_rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        else:
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

        #draw button on screen
        if self.clicked:
            self.clicked = False
            pygame.draw.rect(surface, ('red'), self.rect)
            self.callback()
        else:
            pygame.draw.rect(surface, ('deepskyblue'), self.rect)
        pygame.draw.rect(surface, ('aliceblue'), self.rect, 2)

        # Render and blit the label
        label_surface = self.font.render(self.label, True, (0, 0, 0))
        label_rect = label_surface.get_rect(center=button_rect.center)
        surface.blit(label_surface, label_rect)

        return action

class InputBox():
    def __init__(self, x, y, width, height, initial_text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 255, 255)  # White
        self.active_color = (255, 255, 255)  # White
        self.inactive_color = ('azure2')
        self.text = initial_text
        self.font = pygame.font.Font(None, 32)
        self.active = False
        self.callback = callback
    
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            rect = pygame.Rect(self.rect)
            if rect.collidepoint(event.pos):
                #print("Input box clicked")
                self.active = True
            else:
                self.active = False
        
        if self.active:
            if event.type == pygame.KEYDOWN:
                #print("Input KEYDOWN")
                if event.key == pygame.K_RETURN:
                    #print("Input box return pressed")
                    self.callback(self.text)
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    #print("Input box backspace pressed")
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                return True

        return False

    def draw(self, screen):
        # Draw the input box
        if self.active:
            self.color = self.active_color
        else:
            self.color = self.inactive_color
        pygame.draw.rect(screen, self.color, self.rect)

        # Render the text
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

        # Draw a border around the active input box
        if self.active:
            pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
