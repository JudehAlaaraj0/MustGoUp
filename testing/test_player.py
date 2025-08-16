import unittest
import pygame
from source.model.player import Player
from source.model.platform import Platform
from source.variables import WIDTH, HEIGHT, vec

pygame.init()

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player()
        self.platform = Platform(pos=(WIDTH / 2, HEIGHT - 12))
        self.platform.rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 12, 100, 12)
        self.platforms = [self.platform]

    # W6-1
    def test_initial_state(self):
        self.assertEqual(self.player.vel, vec(0, 0))
        self.assertTrue(self.player.control)
        self.assertFalse(self.player.charging)
        self.assertEqual(self.player.reached, 0)
        self.assertEqual(self.player.highestReached, 0)

    # W6-2
    def test_release_jump_velocity(self):
        self.player.charging = True
        # Manually setting a charge time of half a second
        self.player.charge_start = pygame.time.get_ticks() - 500
        self.player.release_jump()
        # Player should be moving up, as well as can't be charging and doesn't have control
        self.assertLess(self.player.vel.y, 0) 
        self.assertFalse(self.player.charging)
        self.assertFalse(self.player.control)
    
    # W6-3
    def test_manual_rightward_movement(self):
        self.player.control = True
        self.player.charging = False
        self.player.vel.x = 5
        initial_x = self.player.pos.x

        self.player.pos.x += self.player.vel.x

        self.assertGreater(self.player.pos.x, initial_x)

    # W6-4
    def test_manual_leftward_movement(self):
        self.player.control = True
        self.player.charging = False
        self.player.vel.x = -5
        initial_x = self.player.pos.x

        self.player.pos.x += self.player.vel.x

        self.assertLess(self.player.pos.x, initial_x)

    # W6-5
    def test_grounded_gives_control(self):
        self.player.rect.bottom = self.platform.rect.top + 1
        self.player.vel.y = 5
        self.player.check_vertical_collision(self.platforms)
        self.assertTrue(self.player.control)

    # W6-6
    def test_airborne_removes_control(self):
        self.player.rect.bottom = self.platform.rect.top - 20
        self.player.vel.y = 5
        self.player.check_vertical_collision(self.platforms)
        self.assertFalse(self.player.control)

    # B6-7
    def test_start_charge_grounded(self):
        # first must be grounded to charge
        self.player.rect.bottom = self.platform.rect.top + 1
        self.player.vel.y = 5
        self.player.check_vertical_collision(self.platforms)
        # now try charging
        self.player.start_charge(self.platforms)
        self.assertTrue(self.player.charging)

    # B6-8
    def test_start_charge_not_grounded(self):
        # simulating the player falling mid air, putting him above a platform
        self.player.rect.bottom = self.platform.rect.top - 50
        self.player.vel.y = 5
        self.player.check_vertical_collision(self.platforms)
        self.player.start_charge(self.platforms)
        self.assertFalse(self.player.charging)


if __name__ == "__main__":
    unittest.main()