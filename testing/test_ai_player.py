import unittest
import torch
import pygame
from source.model.ai_player import AIPlayer
from source.model.platform import Platform
from source.variables import WIDTH, HEIGHT, vec

pygame.init()

class TestAIPlayer(unittest.TestCase):

    # this set up method is run before each test, 
    # you can find it in the other test classes as well
    def setUp(self):
        self.ai = AIPlayer()
        self.platform = Platform(pos=(WIDTH // 2, HEIGHT - 100))
        self.platforms = [self.platform]


    # W0-1
    def test_brain_structure(self):  
        layers = list(self.ai.brain)
        self.assertEqual(len(layers), 5)
        self.assertIsInstance(layers[0], torch.nn.Linear)
        self.assertEqual(layers[0].in_features, 8)
        self.assertEqual(layers[-1].out_features, 3)

    # W0-2
    def test_mutate_weights(self): 
        # i could copy the weights here with my function,
        # but im testing the mutate_weights function only here.
        # also reminder that this is weights and biases. 
        before = {k: v.clone() for k, v in self.ai.brain.state_dict().items()}
        self.ai.mutate_weights(mutation_rate=0.05)
        after = self.ai.brain.state_dict()
        differences = [not torch.equal(before[k], after[k]) for k in before]
        self.assertTrue(any(differences))

    # W0-3
    def test_copy_weights(self):  
        other = AIPlayer()
        # we set the weights of the first layer AI to a known value
        # so we check if it is actually copying the exact same weights
        other.brain[0].weight.data.fill_(0.5)
        self.ai.copy_weights_from(other)
        for k in other.brain.state_dict():
            self.assertTrue(torch.equal(self.ai.brain.state_dict()[k], other.brain.state_dict()[k]))

    # W0-4
    def test_color(self):
        new_color = (123, 231, 111)
        self.ai.set_color(new_color)
        self.assertEqual(self.ai.get_color(), new_color)

    # B0-5
    def test_get_state_output_shape(self):
        state = self.ai.get_state(self.platforms)
        self.assertIsInstance(state, torch.Tensor)
        self.assertEqual(state.shape, torch.Size([8]))

    # B0-6
    def test_decide_action_range(self): 
        move_x, jump_dir, jump_strength = self.ai.decide_action(self.platforms)
        self.assertTrue(-1 <= move_x <= 1)
        self.assertTrue(-1 <= jump_dir <= 1)
        self.assertTrue(0 <= jump_strength <= 1)

    # B0-7
    def test_collision(self):
        # placing ai on the platform manually
        self.ai.pos = vec(self.platform.rect.centerx, self.platform.rect.top + 1)
        # simulating him falling
        self.ai.vel.y = 5
        self.ai.rect.midbottom = self.ai.pos
        self.ai.rect2.centerx = self.ai.pos.x
        self.ai.rect2.centery = self.ai.rect.centery

        previous_fitness = self.ai.fitness
        self.ai.check_vertical_collision(self.platforms)
        self.assertTrue(self.ai.control)
        # fitness should be increased since he reached a new platform
        self.assertGreaterEqual(self.ai.fitness, previous_fitness)


if __name__ == "__main__":
    unittest.main()