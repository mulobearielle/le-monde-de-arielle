import pygame
from gamePad import BUTTON_MAP

class OptionsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 50)
        self.title_font = pygame.font.Font(None, 74)
        self.options = [
            {"name": "Volume Musique", "value": 50, "type": "slider"},
            {"name": "Volume SFX", "value": 50, "type": "slider"},
            {"name": "Contrôles", "value": None, "type": "menu"},
            {"name": "Retour", "value": None, "type": "action"}
        ]
        self.selected_index = 0
        self.active_slider = None

    def draw_slider(self, option, y_pos):
        slider_width = 200
        slider_rect = pygame.Rect(self.screen.get_width()/2 - 100, y_pos + 10, slider_width, 10)
        pygame.draw.rect(self.screen, (200, 200, 200), slider_rect)
        
        handle_x = slider_rect.left + (option["value"] / 100 * slider_width)
        pygame.draw.circle(self.screen, (0, 255, 0), (int(handle_x), slider_rect.centery), 10)

    def run(self, game):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            self.screen.fill((30, 30, 70))
            
            # Titre
            title_text = self.title_font.render("Options", True, (255, 215, 0))
            title_rect = title_text.get_rect(center=(self.screen.get_width()/2, 100))
            self.screen.blit(title_text, title_rect)
            
            # Options
            for i, option in enumerate(self.options):
                y_pos = 200 + i * 80
                color = (0, 255, 0) if i == self.selected_index else (255, 255, 255)
                
                text = self.font.render(option["name"], True, color)
                text_rect = text.get_rect(center=(self.screen.get_width()/2, y_pos))
                self.screen.blit(text, text_rect)
                
                if option["type"] == "slider":
                    self.draw_slider(option, y_pos)
            
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                # selection au clavier
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                    
                    if event.key == pygame.K_RETURN:
                        if self.options[self.selected_index]["name"] == "Retour":
                            running = False
                    
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

                
                # selection a la souris
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, option in enumerate(self.options):
                        if option["type"] == "slider":
                            slider_rect = pygame.Rect(
                                self.screen.get_width()/2 - 100,
                                200 + i * 80 + 10,
                                200,
                                10
                            )
                            if slider_rect.collidepoint(event.pos):
                                self.active_slider = i
                                value = (event.pos[0] - slider_rect.left) / slider_rect.width * 100
                                self.options[i]["value"] = max(0, min(100, int(value)))
                
                if event.type == pygame.MOUSEMOTION and self.active_slider is not None:
                    i = self.active_slider
                    slider_rect = pygame.Rect(
                        self.screen.get_width()/2 - 100,
                        200 + i * 80 + 10,
                        200,
                        10
                    )
                    value = (event.pos[0] - slider_rect.left) / slider_rect.width * 100
                    self.options[i]["value"] = max(0, min(100, int(value)))
                
                
                if event.type == pygame.MOUSEBUTTONUP:
                    self.active_slider = None

                # selection a la manette
                if event.type == pygame.JOYHATMOTION:
                    x, y = event.value
                    if y == 1:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif y == -1:
                        self.selected_index = (self.selected_index + 1) % len(self.options)

                if event.type == pygame.JOYBUTTONDOWN: #and event.button == 0:  # bouton X
                    mapping = game.gamepad_manager.joystick_mappings.get(
                        event.instance_id, BUTTON_MAP
                    )
                    name = mapping.get(event.button, f"btn_{event.button}")
                    if name == "cross":
                        if self.options[self.selected_index]["name"] == "Retour":
                            running = False
                    elif name == "circle":
                        running = False

            pygame.display.flip()
            clock.tick(30)
        
        # Appliquer les paramètres
        game.music_volume = self.options[0]["value"] / 100
        game.sfx_volume = self.options[1]["value"] / 100
        game.level_up_sound.set_volume(game.sfx_volume)