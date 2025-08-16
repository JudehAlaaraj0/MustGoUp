import pygame
import random
from source.variables import WIDTH, HEIGHT

class Platform(pygame.sprite.Sprite):
    
    def __init__(self, pos, width=100, height=12):
        super().__init__()
        self.surf = pygame.Surface((width, height))
        self.surf.fill((255, 255, 0))
        self.rect = self.surf.get_rect(center=pos)
        self.num = 0

    '''
    Could be a possible addition in future.
    def move(self):
        pass
    '''

    def generate_platforms(count):

        # Each platform has a number
        platNum = 0

        platforms = []

        # Manually creating the first platform, which acts as the ground.
        first_platform = Platform((WIDTH / 2, HEIGHT), width=WIDTH, height=160)
        first_platform.surf.fill((255, 0, 0))
        first_platform.num = platNum
        platNum += 1
        platforms.append(first_platform)

        # I the absolute maximum and minimum the bot can jump, but these values are a bit looser 
        # or it would be way too hard.

        MINIMUM_X_GAP = 175
        MINIMUM_Y_GAP = 175
        MAXIMUM_X_GAP = 200
        MAXIMUM_Y_GAP = 200
        
        # Randomly generate a new platform.
        yGap = random.randint(MINIMUM_Y_GAP, MAXIMUM_Y_GAP) - 100
        currPlatform = Platform((random.randint(50, WIDTH - 50), first_platform.rect.centery - (yGap + first_platform.rect.height)))
        currPlatform.num = platNum
        platforms.append(currPlatform)

        # I manually generate the first actual platform, because the other platforms are generated randomly based off the previous one.
        # This is to ensure that the game remains possible and random.
        for i in range(count - 1):
            platNum = i + 2
            xGap = random.choice([-1,1]) * random.randint(MINIMUM_X_GAP, MAXIMUM_X_GAP)
            yGap = random.randint(MINIMUM_Y_GAP, MAXIMUM_Y_GAP)
            # This condition checks if the platform would go offscreen, and if so, it flips the xGap to the opposite direction.
            if (currPlatform.rect.centerx + xGap <= 50) or (currPlatform.rect.centerx + xGap >= WIDTH - 50):
                xGap *= -1
                currPlatform = Platform((currPlatform.rect.centerx + xGap, currPlatform.rect.centery - yGap))
                currPlatform.num = platNum
                platforms.append(currPlatform)
            else:
                currPlatform = Platform((currPlatform.rect.centerx + xGap, currPlatform.rect.centery - yGap))
                currPlatform.num = platNum
                platforms.append(currPlatform)

        # coloring the last platform purple
        if len(platforms) > 1:
            platforms[-1].surf.fill((157, 0, 255))

        return platforms