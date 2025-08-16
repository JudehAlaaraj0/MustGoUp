import pygame.font

# the only reason this class exists is to save the font path in the same object as the pygame.font class to make
# it easier to use the same font throughout the views.

class GameFont(pygame.font.Font):
    def __init__(self, font_path, size):
        super().__init__(font_path, size)
        self.path = font_path