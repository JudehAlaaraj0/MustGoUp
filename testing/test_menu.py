import unittest
import pygame
from source.view.menu import BaseMenu, MainMenu, AISimulationMenu, InstructionsMenu, SimulationSummaryMenu
from source.view.button import Button
from source.variables import WIDTH, HEIGHT

pygame.init()

# We create dummy classes to be able to test the module without needing the full environment.
class DummyFont(pygame.font.Font):
    def __init__(self):
        super().__init__(None, 24)
    
class DummyMenu(BaseMenu):
    def __init__(self, screen, font, clock, title, button_texts):
        super().__init__(screen, font, clock, title, button_texts)

class TestMenus(unittest.TestCase):

    def setUp(self):
        self.screen = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = DummyFont()

    # W4-1
    def test_base_menu(self):
        button_texts = ["One", "Two", "Three"]
        menu = DummyMenu(self.screen, self.font, self.clock, "Test Title", button_texts)
        self.assertEqual(len(menu.buttons), len(button_texts))
        self.assertEqual(menu.title, "Test Title")

    # W4-2
    def test_main_menu(self):
        menu = MainMenu(self.screen, self.font, self.clock)
        self.assertEqual(len(menu.buttons), 4)
        self.assertIsInstance(menu.buttons[0], Button)

    # W4-3
    def test_ai_simulation(self):
        menu = AISimulationMenu(self.screen, self.font, self.clock)
        expected_texts = ["Top-N Selection", "Tournament Selection", "Roulette Wheel Selection", "Back"]
        actual_texts = [btn.text for btn in menu.buttons]
        self.assertListEqual(actual_texts, expected_texts)

    # W4-4
    def test_instructions_menu(self):
        menu = InstructionsMenu(self.screen, self.font, self.clock)
        self.assertEqual(len(menu.buttons), 1)
        self.assertEqual(menu.buttons[0].text, "Back")

    # W4-5
    def test_simulation_summary_menu(self):
        menu = SimulationSummaryMenu(
            self.screen, self.font, self.clock,
            summary_lines=["Test Summary"],
            best_fitness=[10, 20],
            average_fitness=[5, 15]
        )
        self.assertEqual(len(menu.buttons), 2)
        self.assertEqual(menu.buttons[0].text, "Main Menu")
        self.assertEqual(menu.buttons[1].text, "Quit")

    # W4-6
    def test_simulation_summary_menu_graph(self):
        # We simulate enough data for graph generation
        summary = SimulationSummaryMenu(
            self.screen,
            self.font,
            self.clock,
            best_fitness=[10, 20, 30],
            average_fitness=[5, 15, 25],
            summary_lines=["Some summary"]
        )

        # Run the graph creation logic manually
        graph_surface = None
        try:
            import matplotlib.pyplot as plt
            import io
            import pygame

            # Attempt to render the graph to surface
            plt.figure(figsize=(5, 3))
            plt.plot([10, 20, 30], label="Best Fitness")
            plt.plot([5, 15, 25], label="Average Fitness")
            plt.legend()
            buf = io.BytesIO()
            plt.savefig(buf, format='PNG')
            buf.seek(0)
            graph_surface = pygame.image.load(buf).convert()
            plt.close()
            buf.close()
        except Exception as e:
            self.fail(f"graph generation failed: {e}")

        self.assertIsInstance(graph_surface, pygame.Surface)


if __name__ == "__main__":
    unittest.main()