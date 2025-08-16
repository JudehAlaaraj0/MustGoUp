import unittest
import pygame
from source.view.drawing import Drawing
from source.model.ai_player import AIPlayer
from source.model.platform import Platform
from source.variables import WIDTH, HEIGHT

pygame.init()

class TestDrawing(unittest.TestCase):

    def setUp(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.ai_group = []
        self.platforms = []
        self.all_sprites = pygame.sprite.Group()

        self.bot_low = AIPlayer()
        self.bot_low.pos.y = HEIGHT / 2 + 100
        self.bot_low.highestFitness = 80
        self.bot_low.alive = True

        self.bot_high = AIPlayer()
        self.bot_high.pos.y = HEIGHT / 2 - 100
        self.bot_high.highestFitness = 100
        self.bot_high.alive = True

        self.ai_group.extend([self.bot_low, self.bot_high])
        self.all_sprites.add(self.bot_low, self.bot_high)

        self.platform = Platform(pos=(WIDTH // 2, HEIGHT - 100))
        self.all_sprites.add(self.platforms)

    # W3-1
    def test_get_info(self):  
        highest, highest_alive, highest_pos_alive = Drawing.get_info(self.ai_group)
        self.assertEqual(highest, self.bot_high)
        self.assertEqual(highest_alive, self.bot_high)
        self.assertEqual(highest_pos_alive, self.bot_high)

        # Killing the current highest bot
        self.bot_high.alive = False

        highest, highest_alive, highest_pos_alive = Drawing.get_info(self.ai_group)
        self.assertEqual(highest, self.bot_high)
        self.assertEqual(highest_alive, self.bot_low)
        self.assertEqual(highest_pos_alive, self.bot_low)

    # B3-2
    def test_draw(self):
        try:
            Drawing.draw(self.ai_group, self.platforms, self.all_sprites, self.screen)
        except Exception as e:
            self.fail(f"Drawing.draw() raised an exception: {e}")

    # B3-3
    def test_drawAI(self):
        try:
            font = pygame.font.SysFont(None, 24)
            Drawing.drawAI(self.ai_group, self.platforms, self.all_sprites, self.screen, genNum=2, font=font)
        except Exception as e:
            self.fail(f"Drawing.drawAI() raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()