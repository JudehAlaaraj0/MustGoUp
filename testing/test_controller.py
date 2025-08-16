import unittest
from source.control.controller import Controller
from source.model.ai_player import AIPlayer
import pygame

class TestController(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.players = [AIPlayer() for _ in range(10)]
        for i, p in enumerate(self.players):
            p.fitness = i * 10
    # W2-1
    def test_top_n_selection(self):
        results = [(p, p.fitness) for p in self.players]
        selected = Controller.top_n_selection(results, num_parents=3)
        self.assertEqual(len(selected), 3)
        # since top_n selection guarantees the best we check if the best was chosen.
        self.assertEqual(selected[0][0], self.players[9])

    # W2-2
    def test_tournament_selection(self):
        results = [(p, p.fitness) for p in self.players]
        selected = Controller.tournament_selection(results, num_parents=4, tournament_size=3)
        # returning correct number of players
        self.assertEqual(len(selected), 4)

    # W2-3
    def test_roulette_selection(self):
        results = [(p, p.fitness) for p in self.players]
        selected = Controller.roulette_selection(results, num_parents=5)
        # returning correct number of players
        self.assertEqual(len(selected), 5)

    # B2-4
    def test_generate_random_color(self):
        color = Controller.generate_random_color()
        for c in color:
            # can't have a color too dark since the background is black
            self.assertTrue(50 <= c <= 255)

    # B2-5
    def test_mutate_color(self):
        original = (255, 32, 153)
        mutated = Controller.mutate_color(original)
        for val in mutated:
            # can't have a color too dark since the background is black
            self.assertTrue(50 <= val <= 255)

    # B2-6
    def test_setup(self):
        players = []
        platforms = []
        all_sprites = pygame.sprite.Group()
        player, plats, sprites = Controller.setup(players, platforms, all_sprites)

        # one player
        self.assertEqual(len(player), 1)
        # currently, setup creates 10 platforms only by default since i want to showcase the last platform
        self.assertGreaterEqual(len(plats), 1)
        self.assertGreaterEqual(len(sprites), len(player) + len(plats))

    # B2-7
    def test_setupAI(self):
        ai_group = []
        all_sprites = pygame.sprite.Group()
        ai, platforms, all_sprites = Controller.setupAI(ai_group, all_sprites, population_size=20)

        self.assertEqual(len(ai), 20)
        self.assertEqual(len(all_sprites), 20 + len(platforms))
        for aiplayer in ai:
            self.assertIsInstance(aiplayer, AIPlayer)


if __name__ == "__main__":
    unittest.main()