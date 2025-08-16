import pygame
import sys
import random
import time
import os

from source.view.drawing import Drawing as dr
from source.variables import *
from source.view.menu import *
from source.model.ai_player import AIPlayer
from source.model.player import Player
from source.model.platform import Platform
from source.view.font import GameFont


class Controller:

    def __init__(self, screen, font, clock):
        self.screen = screen
        self.font = font
        self.clock = clock

    @staticmethod
    def top_n_selection(results, num_parents=5):
        results.sort(key=lambda x: x[1], reverse=True)
        return [(p, fit) for p, fit in results[:num_parents]]

    @staticmethod
    def tournament_selection(results, num_parents=5, tournament_size=4):
        selected = []
        for _ in range(num_parents):
            tournament = random.sample(results, tournament_size)
            winner = max(tournament, key=lambda x: x[1])
            selected.append((winner[0], winner[1]))
        return selected

    @staticmethod
    def roulette_selection(results, num_parents=5):
        total_fitness = sum(max(0.001, fit) for _, fit in results)
        selected = []
        for _ in range(num_parents):
            threshold = random.uniform(0, total_fitness)
            curr_sum = 0
            for player, fit in results:
                curr_sum += max(0.001, fit)
                if curr_sum >= threshold:
                    selected.append((player, fit))
                    break
        return selected

    # minimum color value to avoid colors that are too dark, because of black background
    @staticmethod
    def generate_random_color():
        return (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )

    @staticmethod
    def mutate_color(color):
        r = min(255, max(50, color[0] + random.randint(-15, 15)))
        g = min(255, max(50, color[1] + random.randint(-15, 15)))
        b = min(255, max(50, color[2] + random.randint(-15, 15)))
        return (r, g, b)

    # setting up the singular player mode
    @staticmethod
    def setup(players, platforms, all_sprites):
        # this is where you can decide how many platforms you want to generate.
        platforms = Platform.generate_platforms(50)
        for plat in platforms:
            all_sprites.add(plat)
        p1 = Player()
        p1.pos = vec(WIDTH / 2, platforms[0].rect.top)
        players.append(p1)
        all_sprites.add(p1)
        return (players, platforms, all_sprites)

    # setting up the simulation mode
    @staticmethod
    def setupAI(ai_players, all_sprites, parents=None, population_size=100, mutation_rate=0.05):
        # this is where you can decide how many platforms you want to generate.
        platforms_list = Platform.generate_platforms(50)
        for plat in platforms_list:
            all_sprites.add(plat)

        first_platform = platforms_list[0]

        # IMPORTANT here is where parents are chosen, randomly from the selected parents using the selection method.
        # throughout the code, i shortened weights and biases to just weights.
        # if no parents are given, it is the first generation, where most things are random.
        # if parents are given, the AIPlayer copies the weights from the parent and mutates them.
        # The color is also mutated, to showcase that the weights were also mutated.
        for _ in range(population_size):
            aiplayer = AIPlayer()
            if parents is not None and len(parents) > 0:
                chosen_parent, _ = random.choice(parents)
                aiplayer.copy_weights_from(chosen_parent)
                aiplayer.mutate_weights(mutation_rate)
                aiplayer.set_color(Controller.mutate_color(chosen_parent.get_color()))
            else:
                aiplayer.set_color(Controller.generate_random_color())

            # In either case we put them in the middle and sync the rects
            aiplayer.pos = vec(WIDTH / 2, first_platform.rect.top)
            aiplayer.rect.midbottom = aiplayer.pos
            aiplayer.rect2.centerx = aiplayer.pos.x
            aiplayer.rect2.centery = aiplayer.rect.centery

            # add them to the list of players and all_sprites
            ai_players.append(aiplayer)
            all_sprites.add(aiplayer)

        return (ai_players, platforms_list, all_sprites)

    # Game loop for singular player mode.
    def casual_play(self):
        all_sprites = pygame.sprite.Group()
        platforms = []
        players = []
        players, platforms, all_sprites = self.setup(players, platforms, all_sprites)
        p1 = players[0]


        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # user held down space bar, so we start charging the jump
                        p1.start_charge(platforms)
                    elif event.key == pygame.K_q:
                        # user pressed q, so we stop running the game
                        running = False
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        # user released space bar, so we release the jump
                        p1.release_jump()
            # always moving, drawing, and ticking the clock
            # pygame helps us by running this loop 60 times a second at maximum, which is our FPS
            p1.move(platforms)
            dr.draw(players, platforms, all_sprites, self.screen)
            self.clock.tick(FPS)
        # if reached here, user pressed q, go back to the main menu
        self.start_game()

    # Simulation where the generations are ran then analyzed and the simulation summary menu showcases it
    def actual_simulation(self, generations, population_size, time_limit, selection_method):
        best_overall_player = None
        best_overall_fitness = float('-inf')
        parents = []
        best_fitness_per_gen = []
        avg_fitness_per_gen = []

        for gen in range(generations):
            # Results from one generation
            results, user_quit = self.run_generation(population_size, gen, time_limit, parents=parents)

            # Preparing information that will be sent to the summary menu
            results.sort(key=lambda x: x[1], reverse=True)
            fitness_values = [fit for _, fit in results]
            best_fitness = max(fitness_values)
            avg_fitness = sum(fitness_values) / len(fitness_values)
            best_fitness_per_gen.append(best_fitness)
            avg_fitness_per_gen.append(avg_fitness)

            # this isn't used now but could be later.
            best_player = results[0][0]
            if best_fitness > best_overall_fitness:
                best_overall_fitness = best_fitness
                best_overall_player = best_player

            # where the selection method gets applied and we get the parents
            if selection_method == "top_n":
                parents = Controller.top_n_selection(results, num_parents=5)
            elif selection_method == "tournament":
                parents = Controller.tournament_selection(results, num_parents=5)
            elif selection_method == "roulette":
                parents = Controller.roulette_selection(results, num_parents=5)

            if user_quit:
                break

        # the creation of the summary menu
        summary_text = [f"Selection Method: {selection_method}"]
        summary_menu = SimulationSummaryMenu(
            self.screen, self.font, self.clock,
            summary_lines=summary_text,
            best_fitness=best_fitness_per_gen,
            average_fitness=avg_fitness_per_gen
        )
        button_clicked = summary_menu.run()
        if button_clicked == 0:
            # main menu
            self.start_game()
        elif button_clicked == 1:
            pygame.quit()
            sys.exit()

    # function that runs one generation
    def run_generation(self, population_size, gen_num, time_limit, parents=None):
        # these here could also be just normal array.
        all_sprites = pygame.sprite.Group()
        platforms = []
        ai_players = []

        # MUTATION RATE IS CHOSEN HERE FOR THE AI PLAYERS.
        ai_players, platforms, all_sprites = self.setupAI(
            # 0.05 mutation rate is good, 
            # 0.01 is too low, 
            # 0.1 is also good, 
            # but 0.2 is good, 
            # 0.3 is good,
            # 0.4 is good but a bit too much,
            # 0.5 is too much
            # 0.05 is the "strictest" mutation rate, mutating only a little bit but still producing good results.
            # going above 0.3 is a bit harmful
            ai_players, all_sprites, parents=parents, population_size=population_size, mutation_rate=0.2
        )

        start_time = time.time()
        alive_players = list(ai_players)
        done = False
        user_quit = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        user_quit = True
                        done = True

            # move all the players 
            for ap in alive_players:
                ap.move(platforms)

            elapsed = time.time() - start_time
            alive_players = [p for p in alive_players if p.alive]

            # we end the generation if the time limit is reached or all players are dead
            if elapsed >= time_limit or not alive_players:
                done = True
            else:
                # else we contiinue drawing and the simulation
                dr.drawAI(ai_players, platforms, all_sprites, self.screen, gen_num, self.font)
                self.clock.tick(FPS)

        # returning the results of the generation.
        results = [(ap, ap.fitness) for ap in ai_players]
        return results, user_quit

    # the main function that runs the game, it is the entry point of the game with all the menus and gameplay
    def start_game(self):
        menu = MainMenu(self.screen, self.font, self.clock)
        button_clicked = menu.run()

        # MAIN SETTINGS FOR SIMULATION
        time_limit = 20
        # POPULATION SIZE SHOULD BE MINIMUM OF WHATEVER TOURNAMENT SIZE IS, OR IT WILL NOT WORK
        population_size = 100
        number_of_generations = 150

        if button_clicked == 0:
            self.casual_play()
        elif button_clicked == 1:
            ai_menu = AISimulationMenu(self.screen, self.font, self.clock)
            ai_button_clicked = ai_menu.run()
            if ai_button_clicked == 0:
                self.actual_simulation(number_of_generations, population_size, time_limit, selection_method="top_n")
            elif ai_button_clicked == 1:
                self.actual_simulation(number_of_generations, population_size, time_limit, selection_method="tournament")
            elif ai_button_clicked == 2:
                self.actual_simulation(number_of_generations, population_size, time_limit, selection_method="roulette")
            elif ai_button_clicked == 3:
                self.start_game()
        elif button_clicked == 2:
            instructions = InstructionsMenu(self.screen, self.font, self.clock)
            instructions.run()
            self.start_game()
        elif button_clicked == 3:
            pygame.quit()
            sys.exit()

if __name__ == "__main__":

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # checking if sound file is present
    sound_check_path = os.path.join(base_dir, "assets", "sounds", "click.mp3")
    if not os.path.exists(sound_check_path):
        raise FileNotFoundError(f"Missing sound file at {sound_check_path}")
    
    # checking if font file is present
    font_path = os.path.join(base_dir, "assets", "font", "Pixellari.ttf")
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Missing font file at {font_path}")

    # initializing pygame and creating the controller
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Must Go Up!")
    font = GameFont(font_path, 27)
    clock = pygame.time.Clock()

    # creating the controller and starting the main function.
    c = Controller(screen, font, clock)
    c.start_game()