import pygame
from source.variables import WIDTH, HEIGHT

# Drawing class to handle all the drawing of the game
class Drawing:

    def __init__(self):
        pass

    @staticmethod
    def get_info(ai_players):

        highest_bot = None
        highest_bot_alive = None
        highest_position_bot_alive = None

        for ap in ai_players:
            # highest overall fitness
            if highest_bot is None or ap.highestFitness > highest_bot.highestFitness:
                highest_bot = ap

            if ap.alive:
                # highest fitness among alive players
                if highest_bot_alive is None or ap.highestFitness > highest_bot_alive.highestFitness:
                    highest_bot_alive = ap

                # highest position among alive players (lowest y value)
                if highest_position_bot_alive is None or ap.pos.y < highest_position_bot_alive.pos.y:
                    highest_position_bot_alive = ap

        return highest_bot, highest_bot_alive, highest_position_bot_alive
    
    # drawing function for the single player mode
    @staticmethod
    def draw(players, platforms, all_sprites, screen):
        # getting the singular player
        p1 = players[0]
        # the camera follows the player
        camera_offset_y = p1.pos.y - HEIGHT / 2
        screen.fill("black")

        # looping and drawing the entities, everything adjusted by the camera offset, so we follow the player
        for entity in all_sprites:
                # the player
                if entity in players:
                    draw_rect1 = entity.rect.copy()
                    draw_rect1.y -= int(camera_offset_y)
                    
                    draw_rect2 = entity.rect2.copy()
                    draw_rect2.y -= int(camera_offset_y)
                    
                    screen.blit(entity.surf1, draw_rect1)
                    screen.blit(entity.surf2, draw_rect2)
                # platforms
                elif entity in platforms:
                    draw_rect = entity.rect.copy()
                    draw_rect.y -= int(camera_offset_y)
                    screen.blit(entity.surf, draw_rect)
                '''
                else:
                    # Possibile additions in future
                '''
        pygame.display.update()

    # drawing function for the ai simulation mode
    @staticmethod
    def drawAI(ai_players, platforms, all_sprites, screen, genNum, font):
        screen.fill("black")

        # Title
        title_surf = font.render("AI Simulation", True, "white")
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 20))
        screen.blit(title_surf, title_rect)

        # getting specific information
        highest_bot, highest_bot_alive, highest_position_bot_alive = Drawing.get_info(ai_players)

        # drawing some information about the current generation
        if highest_bot is not None:
            info_text = f"Gen Num {genNum + 1}, highest fitness this gen={highest_bot.highestFitness:.2f}"
            info_surf = font.render(info_text, True, (255, 255, 255))
            # positioning text to top left of screen
            screen.blit(info_surf, (10, 40))

        # the camera follows the highest position bot that is alive currently.
        camera_offset_y = highest_position_bot_alive.pos.y - HEIGHT / 2
        
        # looping through the entities and drawing their rects, everything adjusted by the camera offset, 
        # so we follow the highest bot alive
        for entity in all_sprites:
            # Alive AI Players
            if entity in ai_players and entity.alive == True:
                draw_rect1 = entity.rect.copy()
                draw_rect1.y -= int(camera_offset_y)

                draw_rect2 = entity.rect2.copy()
                draw_rect2.y -= int(camera_offset_y)

                screen.blit(entity.surf1, draw_rect1)
                screen.blit(entity.surf2, draw_rect2)

            # Platforms
            elif entity in platforms:
                if entity == highest_position_bot_alive.nextPlat:
                    draw_rect = entity.rect.copy()
                    draw_rect.y -= int(camera_offset_y)
                    pygame.draw.rect(screen, (255, 255, 255), draw_rect)
                else:
                    draw_rect = entity.rect.copy()
                    draw_rect.y -= int(camera_offset_y)
                    screen.blit(entity.surf, draw_rect)
            '''
            # This could exist if more entities are added in the future
            else:
                draw_rect = entity.rect.copy()
                draw_rect.y -= int(camera_offset_y)
                displaysurface.blit(entity.surf, draw_rect)'
            '''
        # actually udpates the display
        pygame.display.update()