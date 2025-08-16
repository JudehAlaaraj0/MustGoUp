import unittest
import pygame
import os
from source.view.button import Button

pygame.init()
# Dummy display for testing
pygame.display.set_mode((800, 600))

class TestButton(unittest.TestCase):

    def setUp(self):
        self.screen = pygame.display.get_surface()
        self.font = pygame.font.SysFont("Arial", 27)
        self.button = Button(
            text="Testing Button",
            pos=(100, 100),
            screen=self.screen,
            font=self.font,
            width=200,
            height=50
        )

    # W1-1
    def test_button_properties(self):  
        self.assertEqual(self.button.text, "Testing Button")
        self.assertEqual(self.button.pos, (100, 100))
        self.assertEqual(self.button.width, 200)
        self.assertEqual(self.button.height, 50)
        self.assertIsNotNone(self.button.button)

    # B1-2
    def test_check_clicked_returns_false(self): 
        self.assertFalse(self.button.check_clicked())

    # B1-3
    def test_check_clicked_by_mouse(self):  
        # Simulate mouse over button and left click
        # IMPORTANT, the test will fail if the mouse is not already over the windows that pops up
        # So hover your mouse near the middle of the monitor before running the test, or if you're reading this now
        # you know how to fix the problem
        pygame.mouse.set_pos((150, 125))

        # saving the original get_pressed method to restore it later
        original_get_pressed = pygame.mouse.get_pressed
        # Override mouse.get_pressed to simulate click state
        pygame.mouse.get_pressed = lambda: (1, 0, 0)

        try:
            result = self.button.check_clicked()
        finally:
            pygame.mouse.get_pressed = original_get_pressed
            pygame.event.clear()

        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()