import unittest
from source.model.platform import Platform
from source.variables import WIDTH, HEIGHT

class TestPlatform(unittest.TestCase):

    # W5-1
    def test_generate_platform_count(self):
        count = 10
        platforms = Platform.generate_platforms(count)
        # Check if the number of platforms generated is equal to count + 1, since the
        # ground platform doesn't count towards the number of actual obstacle platforms.
        self.assertEqual(len(platforms), count + 1) 
    
    # W5-2
    def test_first_platform(self):
        platforms = Platform.generate_platforms(5)
        first = platforms[0]
        self.assertEqual(first.rect.width, WIDTH)
        self.assertEqual(first.rect.height, 160)
        self.assertEqual(first.rect.centerx, WIDTH // 2)
        self.assertEqual(first.rect.centery, HEIGHT)

    # W5-3
    def test_last_platform(self):
        platforms = Platform.generate_platforms(5)
        last_platform = platforms[-1]
        last_pixel_color = last_platform.surf.get_at((0, 0))
        self.assertEqual(last_pixel_color[:3], (157, 0, 255))

    # W5-4
    def test_platform_numbering(self):
        count = 5
        platforms = Platform.generate_platforms(count)
        # the ground platform should have a num of 0
        for i, plat in enumerate(platforms):
            self.assertEqual(plat.num, i)

    # B5-5
    def test_platforms_within_bounds(self):
        platforms = Platform.generate_platforms(20)
        for platform in platforms:
            self.assertGreaterEqual(platform.rect.left, 0)
            self.assertLessEqual(platform.rect.right, WIDTH)

if __name__ == "__main__":
    unittest.main()