import os
import pygame

class Button:
    def __init__(self, text, pos, screen, font, width=400, height=50,
                 color_normal="white", color_hover="#dddddd",
                 text_color="black", hover_text_color="black"):
        self.text = text
        self.pos = pos
        self.width = width
        self.height = height
        self.screen = screen
        self.font = font
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.text_color = text_color
        self.hover_text_color = hover_text_color
        self.button = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)

        # sound
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        sound_path = os.path.join(base_dir, "assets", "sounds", "click.mp3")
        if os.path.exists(sound_path):
            self.click_sound = pygame.mixer.Sound(sound_path)
            self.click_sound.set_volume(0.4)
        else:
            self.click_sound = None

    def draw(self):
        # Draws the button on the screen, and if hovered, theres a slight color change to show that.
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.button.collidepoint(mouse_pos)

        fill_color = self.color_hover if is_hovered else self.color_normal
        text_color = self.hover_text_color if is_hovered else self.text_color

        # This is for a slight shadow effect on the buttons
        shadow_offset = 3
        shadow_rect = self.button.move(shadow_offset, shadow_offset)
        pygame.draw.rect(self.screen, (30,30,30), shadow_rect, border_radius=4)

        # Button and border
        pygame.draw.rect(self.screen, fill_color, self.button, border_radius=4)
        # border makes the shadow effect more visible, looks better simply
        pygame.draw.rect(self.screen, "black", self.button, 2, border_radius=4)

        # Text
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.button.center)
        self.screen.blit(text_surface, text_rect)

    # Runs in the menu loop to check if the button is clicked
    def check_clicked(self):
        if self.button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            if self.click_sound:
                self.click_sound.play()
            return True
        return False