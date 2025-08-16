import pygame
from pygame.locals import *
from source.variables import *

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Yellow vertical collision detection
        self.surf1 = pygame.Surface((24, 30))
        self.surf1.fill((255, 255, 0))
        self.rect = self.surf1.get_rect()

        # Purple horizontal collision detection.
        self.surf2 = pygame.Surface((30, 24))
        self.surf2.fill((255, 0, 255))
        self.rect2 = self.surf2.get_rect()

        self.pos = vec(WIDTH / 2, HEIGHT - 12)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.charging = False
        self.charge_start = 0
        self.horiz_speed = 5
        self.max_fall_speed = 10

        self.control = True


        self.rect.midbottom = self.pos
        self.rect2.centerx = self.pos.x
        self.rect2.centery = self.rect.centery

        # a bot remembers where it is at and its highest platform reached
        self.reached = 0
        self.highestReached = 0

    def move(self, platforms):
        # Gravity
        self.acc = vec(0, 0.5)

        # horizontal movement
        pressed_keys = pygame.key.get_pressed()
        if not self.charging:
            if self.control:
                if pressed_keys[K_LEFT]:
                    self.vel.x = -self.horiz_speed
                elif pressed_keys[K_RIGHT]:
                    self.vel.x = self.horiz_speed
                else:
                    self.vel.x = 0
        else:
            self.vel.x = 0

        # Update horizontal position
        self.pos.x += self.vel.x

        # Wrapping around the screen horizontally.
        if self.pos.x > WIDTH:
            self.pos.x = 0
        elif self.pos.x < 0:
            self.pos.x = WIDTH

        # Update the purple rect for horizontal collision.
        self.rect2.centerx = self.pos.x
        self.check_horizontal_collision(platforms)

        # vertical movement, limited to a certain speed to prevent clipping through platforms and simply going too fast.
        self.vel.y += self.acc.y
        if self.vel.y > self.max_fall_speed:
            self.vel.y = self.max_fall_speed

        # Update vertical position.
        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.rect.midbottom = (self.pos.x, self.pos.y)
        # Syncing both yellow and purple rectangles.
        self.rect2.centery = self.rect.centery
        self.check_vertical_collision(platforms)


    def check_horizontal_collision(self, platforms):
        for plat in platforms:
            if self.rect2.colliderect(plat.rect):
                # Moving right
                if self.vel.x > 0:  
                    self.pos.x = plat.rect.left - self.rect2.width / 2
                # Moving left
                elif self.vel.x < 0:  
                    self.pos.x = plat.rect.right + self.rect2.width / 2
                self.rect2.centerx = self.pos.x
                # Reverse horizontal momentum
                self.vel.x = -self.vel.x  

    def check_vertical_collision(self, platforms):
        grounded = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                # Falling down onto a platform, the second condition is to eliminate the edge case of top corners of players
                # Clipping the bottom of a platform when they are diagonally falling down.
                if self.vel.y > 0 and plat.rect.top > self.rect.top:  
                    self.pos.y = plat.rect.top
                    self.vel.y = 0
                    self.reached = plat.num
                    if self.reached > self.highestReached:
                        self.highestReached = self.reached
                    grounded = True
                # Moving upward into a platform.
                elif self.vel.y < 0:  
                    self.pos.y = plat.rect.bottom + self.rect.height
                    self.vel.y = 0
                self.rect.midbottom = (self.pos.x, self.pos.y)
                self.rect2.centery = self.rect.centery
        self.control = grounded
        

    def start_charge(self, platforms):
        # Allow jump charging only if player is on the ground 
        if self.control:
            self.charging = True
            self.charge_start = pygame.time.get_ticks()
            # Freeze horizontal movement.
            self.vel.x = 0

    def release_jump(self):

        if self.charging:
            # Getting jump strength based on charge duration.
            charge_duration = (pygame.time.get_ticks() - self.charge_start) / 1000.0
            max_charge = 1.0
            charge_duration = min(charge_duration, max_charge)
            jump_strength = 5 + (13 * (charge_duration / max_charge))
            # important for jump direction
            pressed_keys = pygame.key.get_pressed()
            horizontal_speed = 0
            # setting the velocities based on the new jump info
            if pressed_keys[K_LEFT]:
                horizontal_speed = -self.horiz_speed
            elif pressed_keys[K_RIGHT]:
                horizontal_speed = self.horiz_speed
            self.vel.y = -jump_strength
            self.vel.x = horizontal_speed
            # player loses control and no longer charging
            self.charging = False
            self.control = False