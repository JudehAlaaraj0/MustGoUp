import pygame
from source.view.button import Button
import sys
from abc import ABC
from source.variables import FPS
import matplotlib
# this is to avoid a glitch with matplotlib and pygame affecting the screen
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import io
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm


# Abstract class for menus, contains some styling and button logic
class BaseMenu(ABC):
    def __init__(self, screen, font, clock, title, button_texts):
        self.screen = screen
        self.font = font
        self.clock = clock
        self.title = title
        self.width = screen.get_width()
        self.height = screen.get_height()

        button_width = 400
        button_height = 50
        spacing = 20

        total_height = len(button_texts) * button_height + (len(button_texts) - 1) * spacing
        start_y = (self.height - total_height) // 2

        self.buttons = []
        for i, text in enumerate(button_texts):
            btn_x = (self.width - button_width) // 2
            btn_y = start_y + i * (button_height + spacing)
            self.buttons.append(Button(text, (btn_x, btn_y), self.screen, self.font,
                                       width=button_width, height=button_height))
            
        # the reason I need wait for a mouse release is because from one menu to the next, pygame still recognizes the mouse as pressed
        # so sometimes the button behind the current one in the next menu will be clicked automatically.
        self.wait_for_mouse_release()

    def wait_for_mouse_release(self):
        while pygame.mouse.get_pressed()[0]:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.time.delay(10)

    def draw_title_with_shadow(self):
        # Shadow
        shadow_surf = self.font.render(self.title, True, "gray")
        shadow_rect = shadow_surf.get_rect(center=(self.width // 2 + 2, 52))
        self.screen.blit(shadow_surf, shadow_rect)

        # Main title
        title_surf = self.font.render(self.title, True, "white")
        title_rect = title_surf.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title_surf, title_rect)

    # Each menu has a loop which runs till the user clicks a button
    def run(self):
        running = True
        clicked_button = None
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill("black")

            self.draw_title_with_shadow()

            for index, button in enumerate(self.buttons):
                button.draw()
                if button.check_clicked():
                    clicked_button = index
                    running = False

            pygame.display.flip()
            self.clock.tick(FPS)

        return clicked_button


class MainMenu(BaseMenu):
    def __init__(self, screen, font, clock):
        super().__init__(screen, font, clock, "Must Go Up!", ["Casual Play", "AI Simulation", "Instructions", "Quit"])

class AISimulationMenu(BaseMenu):
    def __init__(self, screen, font, clock):
        super().__init__(screen, font, clock, "Choose Selection Method", [
            "Top-N Selection",
            "Tournament Selection",
            "Roulette Wheel Selection",
            "Back"
        ])

# We override the methods to adjust the button position and write the instructions
class InstructionsMenu(BaseMenu):
    def __init__(self, screen, font, clock):
        self.screen = screen
        self.font = font
        self.clock = clock
        self.title = "Instructions"
        self.width = screen.get_width()
        self.height = screen.get_height()

        button_width = 200
        button_height = 50
        btn_x = (self.width - button_width) // 2
        btn_y = self.height - button_height - 40

        self.buttons = [
            Button("Back", (btn_x, btn_y), self.screen, self.font, width=button_width, height=button_height)
        ]

        self.wait_for_mouse_release()

    def run(self):
        running = True
        clicked_button = None

        instructions = [
            "Welcome to Must Go Up!",
            "In casual play:",
            "- Use LEFT and RIGHT arrow keys to move.",
            "- Hold SPACE to charge a jump, release to jump.",
            "- Combine LEFT/RIGHT with SPACE to jump diagonally.",
            "- Press Q to return to main menu.",
            "",
            "In AI Simulation mode:",
            "- AI learns to play the game!",
            "- Press Q to end early and see results."
        ]

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill("black")

            # Title plus shadow
            self.draw_title_with_shadow()

            # Instructions
            small_font = pygame.font.Font(self.font.path, 20)
            for i, line in enumerate(instructions):
                line_surf = small_font.render(line, True, "white")
                self.screen.blit(line_surf, (60, 100 + i * 28))

            for index, button in enumerate(self.buttons):
                button.draw()
                if button.check_clicked():
                    clicked_button = index
                    running = False

            pygame.display.flip()
            self.clock.tick(FPS)

        return clicked_button

# This menu contains the graph of the simulation results and the buttons to go back to the main menu or quit
class SimulationSummaryMenu(BaseMenu):
    def __init__(self, screen, font, clock, summary_lines=None, best_fitness=None, average_fitness=None):
        self.screen = screen
        self.font = font
        self.clock = clock
        self.title = "Simulation Summary"
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.best_fitness = best_fitness
        self.average_fitness = average_fitness

        self.summary_lines = summary_lines if summary_lines else ["Simulation complete."]

        button_width = 200
        button_height = 50
        spacing = 20
        start_y = self.height - (2 * button_height + spacing) - 40

        self.buttons = [
            Button("Main Menu", (self.width // 2 - button_width // 2, start_y), self.screen, self.font, width=button_width, height=button_height),
            Button("Quit", (self.width // 2 - button_width // 2, start_y + button_height + spacing), self.screen, self.font, width=button_width, height=button_height)
        ]

        self.wait_for_mouse_release()

    def run(self):
        running = True
        clicked_button = None
        graph_surface = None
        show_message_instead = False

        # If we have fitness data, we create the graph
        if self.best_fitness and len(self.best_fitness) >= 2:
            font_path = self.font.path

            # Custom font needs new font sizes
            font_title = fm.FontProperties(fname=font_path, size=18)
            font_labels = fm.FontProperties(fname=font_path, size=16)
            font_ticks = fm.FontProperties(fname=font_path, size=14)
            font_legend = fm.FontProperties(fname=font_path, size=14)

            plt.figure(figsize=(10, 5))

            # Setting new colors for axies and labels
            axi = plt.gca()
            axi.set_facecolor('white')
            axi.tick_params(axis='x', colors='black')
            axi.tick_params(axis='y', colors='black')
            axi.spines['bottom'].set_color('black')
            axi.spines['top'].set_color('black')
            axi.spines['left'].set_color('black')
            axi.spines['right'].set_color('black')

            # Plot lines
            # This is to show the first generation as 1 instead of 0
            generations = list(range(1, len(self.best_fitness) + 1))
            plt.plot(generations, self.best_fitness, label='Best Fitness', color='green', linewidth=2)
            plt.plot(generations, self.average_fitness, label='Average Fitness', color='blue', linestyle='--', linewidth=2)


            # Labels and title
            plt.xlabel("Generation", fontproperties=font_labels, color='black')
            plt.ylabel("Fitness", fontproperties=font_labels, color='black')
            plt.title("Fitness Over Generations", fontproperties=font_title, color='black')

            # This is so we don't get fractions of generations on the graph which is impossible
            axi.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

            # applying font to tick labels
            for label in axi.get_xticklabels() + axi.get_yticklabels():
                label.set_fontproperties(font_ticks)
                label.set_color('black')

            # legend with font and color
            legend = plt.legend(prop=font_legend)
            for text in legend.get_texts():
                text.set_color('black')
            legend.get_frame().set_edgecolor('black')
            legend.get_frame().set_facecolor('white')

            plt.tight_layout()

            # putting the plot in a pygame surface to display it
            buf = io.BytesIO()
            plt.savefig(buf, format='PNG', dpi=300)
            buf.seek(0)
            graph_surface = pygame.image.load(buf).convert()
            graph_surface = pygame.transform.scale(graph_surface, (700, 400))
            buf.close()
            plt.close()
        else:
            # If we don't have data, we show a message instead of the graph
            show_message_instead = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill("black")

            # Title
            self.draw_title_with_shadow()

            # Summary lines, for now it's just the selection method
            small_font = pygame.font.Font(self.font.path, 20)
            for i, line in enumerate(self.summary_lines):
                text_surf = small_font.render(line, True, "white")
                self.screen.blit(text_surf, (60, 100 + i * 30))

            # Graph or warning message
            if graph_surface:
                graph_rect = graph_surface.get_rect(center=(self.width // 2, 370))
                self.screen.blit(graph_surface, graph_rect)
            elif show_message_instead:
                fallback_msg = "Run the simulation for at least a couple generations to see statistics!"
                msg_surface = small_font.render(fallback_msg, True, "white")
                msg_rect = msg_surface.get_rect(center=(self.width // 2, 360))
                self.screen.blit(msg_surface, msg_rect)

            # Buttons
            for index, button in enumerate(self.buttons):
                button.draw()
                if button.check_clicked():
                    clicked_button = index
                    running = False

            pygame.display.flip()
            self.clock.tick(FPS)

        return clicked_button