import random
import torch
import torch.nn as nn

from source.variables import *
from source.model.player import Player

class AIPlayer(Player):

    def __init__(self):
        super().__init__()

        self.fitness = 0
        self.highestFitness = 0
        self.alive = True
        self.nextPlat = None
        self.firstJump = True
        self.color = None

        # neural network
        self.brain = nn.Sequential(
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, 16),
            nn.ReLU(),
            nn.Linear(16, 3)
        )

    def set_color(self, color):
        self.color = color
        self.surf1.fill(color)
        self.surf2.fill(color)

    def get_color(self):
        return self.color

    # function that gets the current state of bot, basically the required inputs for the neural network.
    def get_state(self, platforms):

        # getting the next platform to jump to
        next_plat = None
        min_dist = float('inf')
        for plat in platforms:
            # reminder that the y pos decreases as you go up in pygame in all cases.
            # so we are looking for the closest platform above the bot even though we are checking for
            # plat.rect.top < self.pos.y the plat rect top is at a greater height than self.pos.y.
            if plat.rect.top < self.pos.y:
                dist = self.pos.y - plat.rect.top
                if dist < min_dist:
                    min_dist = dist
                    next_plat = plat
                    self.nextPlat = next_plat

        # in case no platforms are found (reached the top), set the position to the bot's position.
        next_plat_x = self.pos.x
        next_plat_y = self.pos.y
        next_plat_left = self.pos.x
        next_plat_right = self.pos.x

        if next_plat:
            next_plat_x = next_plat.rect.centerx
            next_plat_y = next_plat.rect.top
            next_plat_left = next_plat.rect.left
            next_plat_right = next_plat.rect.right

        # this is how the neural network inputs are structured:
        state = torch.tensor([
            self.pos.x,
            self.pos.y,
            next_plat_x,
            next_plat_y,
            self.vel.x,
            self.vel.y,
            next_plat_left,
            next_plat_right
        ], dtype=torch.float32)

        return state

    def decide_action(self, platforms):

        # getting the input state for the brain
        state = self.get_state(platforms)
        # getting the output from the brain using the state as input
        output = self.brain(state)

        # normalizing the outputs
        move_x = torch.tanh(output[0])
        jump_dir = torch.tanh(output[1])
        jump_strength = torch.sigmoid(output[2])

        # this is to promote exploration
        exploration_scale = 0.1
        move_x += random.uniform(-exploration_scale, exploration_scale)
        jump_dir += random.uniform(-exploration_scale, exploration_scale)
        jump_strength += random.uniform(-exploration_scale, exploration_scale)

        # fixing after exploration scaling
        move_x = max(-1, min(1, move_x))
        jump_dir = max(-1, min(1, jump_dir))
        jump_strength = max(0, min(1, jump_strength))

        move_x = move_x.item() if isinstance(move_x, torch.Tensor) else move_x
        jump_dir = jump_dir.item() if isinstance(jump_dir, torch.Tensor) else jump_dir
        jump_strength = jump_strength.item() if isinstance(jump_strength, torch.Tensor) else jump_strength

        return move_x, jump_dir, jump_strength

    def move(self, platforms):
        # simulating gravity
        self.acc = vec(0, 0.5)

        # self.control means on the ground.
        if self.control:

            # getting outputs
            move_x, jump_dir, jump_strength = self.decide_action(platforms)

            # setting the horizontal movement
            if abs(move_x) > 0.2:
                self.vel.x = -self.horiz_speed if move_x < 0 else self.horiz_speed

            # bot wants to jump, lower value could be used
            if jump_strength > 0.5:

                # rewarding the first jump
                if self.firstJump:
                    self.fitness += 30
                    self.firstJump = False

                # applying a jump penalty to help the bot learn precise jumps
                jumpPenalty = (jump_strength ** 3 * 5)
                self.fitness -= jumpPenalty

                # Making minnimum fitness 0, no negatives.
                self.fitness = max(0, self.fitness)

                # Just reducing max jump height REMARK: the bots can still overshoot jumps, they still have to regulate jump strength
                # to avoid overshooting. This is to help teach the neural network not always to use max jump height.
                if jump_strength > 0.9:
                    jump_strength = 0.8
                
                # applying the choices to the volocities.
                scaled_strength = 5 + (13 * (jump_strength / 1.0))
                horizontal_speed = 0

                # setting jump direction and velocities and losing control
                if jump_dir < -0.2:
                    horizontal_speed = -self.horiz_speed
                elif jump_dir > 0.2:
                    horizontal_speed = self.horiz_speed
                self.vel.y = -scaled_strength
                self.vel.x = horizontal_speed
                self.control = False

        # actually moving the bot horizontally
        self.pos.x += self.vel.x

        # we remove the bot from the game if it goes out of bounds
        if self.pos.x > WIDTH or self.pos.x < 0:
            self.alive = False

        # making sure the rect responsible for horizontal movement is centered then checking horizontal collision
        self.rect2.centerx = self.pos.x
        self.check_horizontal_collision(platforms)

        # applying vertical movement to velocity
        self.vel.y += self.acc.y
        if self.vel.y > self.max_fall_speed:
            self.vel.y = self.max_fall_speed

        # actually changing the vertical position then checking vertical collision
        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.rect.midbottom = (self.pos.x, self.pos.y)
        self.rect2.centery = self.rect.centery
        self.check_vertical_collision(platforms)

    def check_vertical_collision(self, platforms):
        self.control = False

        for plat in platforms:
            if self.rect.colliderect(plat.rect):

                # Falling down onto a platform, the condition after and is to eliminate the edge case of top corners of players
                # Clipping the bottom of a platform when they are diagonally falling down.
                if self.vel.y > 0 and plat.rect.top > self.rect.top:
                    self.pos.y = plat.rect.top
                    self.vel.y = 0
                    self.rect.midbottom = (self.pos.x, self.pos.y)
                    self.rect2.centery = self.rect.centery
                    # rewarding the bot for reaching a new high platform
                    self.reached = plat.num
                    if self.reached > self.highestReached:
                        self.fitness += 100
                        self.highestReached = self.reached
                    if self.fitness > self.highestFitness:
                        self.highestFitness = self.fitness
                        # since the bot truly landed, we give it control again
                    self.control = True
                # moving upward into a platform.
                elif self.vel.y < 0:
                    # make the bot fall down after bumping its head
                    self.pos.y = plat.rect.bottom + self.rect.height
                    self.vel.y = 0
                    self.rect.midbottom = (self.pos.x, self.pos.y)
                    self.rect2.centery = self.rect.centery

    def mutate_weights(self, mutation_rate=0.01):
        # we are not using any back propagation, so no need to track gradients
        with torch.no_grad():
            for param in self.brain.parameters():
                # we have 6 params, the 3 weights and 3 biases
                param += torch.randn_like(param) * mutation_rate

    def copy_weights_from(self, parent):
        # puts the copy of weights from the parent bot to the child bot. 
        self.brain.load_state_dict(parent.brain.state_dict())

    def inspect_weights(self):
        # this function inspects the first layer's weights,
        # not used in the program but was useful for understanding weights.
        first_linear = self.brain[0]
        weights = first_linear.weight.data

        input_names = [
            "self_pos_x",
            "self_pos_y",
            "next_plat_x",
            "next_plat_y",
            "self_vel_x",
            "self_vel_y",
            "next_plat_left",
            "next_plat_right"
        ]

        print("FIRST LAYER WEIGHTS")
        for i, name in enumerate(input_names):
            col_weights = weights[:, i]
            # high mean means strong influence
            mean_val = col_weights.mean().item()
            # high standard deviation means the same neuron varies in importance among the output neurons.
            std_val = col_weights.std().item()
            print(f"input name = '{name}' (column {i}): Mean: {mean_val:.4f}, Std: {std_val:.4f}")
            print(f"  Weights: {col_weights.tolist()}")
            print("-" * 20)