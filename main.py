import pygame
import sys
from Game import Game
from level_menu import LevelMenu
from option import OptionsMenu
from gamePad import BUTTON_MAP, GamepadManager


def main():
    

    pygame.init()
    pygame.font.init()

    # Créer la fenêtre
    # Plein-écran à la résolution du bureau
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    screen = pygame.display.set_mode(
        (screen_width-155, screen_height-155),
        pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
    )

    print("Taille réelle de l'écran :", screen_width, "x", screen_height)
    pygame.display.set_caption("L'univers d'Arielle")

    
    
    # Initialisation des composants
    game, level_menu, options_menu = initialize_components(screen)
    
    
    
    # Nouveau : Afficher l'introduction générale
    game.show_game_intro()

    # État courant
    current_screen = "main_menu"  # main_menu/level_menu/options/game
    clock = pygame.time.Clock()
    running = True

    while running:
        # Gestion des écrans
        if current_screen == "main_menu":
            action = show_main_menu(screen, game)
            if action == "commencer":
                current_screen = "level_menu"
            elif action == "options":
                current_screen = "options"
            elif action == "réinitialiser":
                level_menu.reset_progress()
            elif action == "quitter":
                running = False

        elif current_screen == "level_menu":
            game.menu_context = "level_menu"
            result = level_menu.run()
            if result == "exit":
                # Retour au menu principal si Échap ou fermeture
                current_screen = "main_menu"
            if isinstance(result, int):
                # Lancement du niveau sélectionné
                game.current_level = result
                game.initialize_game_state()
                game_result = game.game_loop()
                if game_result:
                    level_menu.complete_level(game.current_level)
                current_screen = "level_menu"  # Retour au menu de niveaux

        elif current_screen == "options":
            game.menu_context = "options_menu"
            options_menu.run(game)
            current_screen = "main_menu"

        # Limiter la boucle
        clock.tick(60)

    pygame.quit()
    sys.exit()


def initialize_components(screen):
    """Initialise les composants du jeu."""
    game = Game(screen)
    level_menu = LevelMenu(screen, game)
    options_menu = OptionsMenu(screen)
    game.level_menu = level_menu
    game.options_menu = options_menu
    level_menu.game = game
    options_menu.game = game
    return game, level_menu, options_menu


def show_main_menu(screen, game):
    """Affiche le menu principal et retourne l'action choisie."""
    font = pygame.font.Font(None, 50)
    options = ["Commencer", "Options", "Réinitialiser", "Quitter"]
    selected = 0

    while True:
        render_main_menu(screen, font, options, selected)
        # 1) Purge manuelle avant lecture
        pygame.event.pump()
        # 2) Récupération sécurisée de la file d'événements
        try:
            events = pygame.event.get()
        except Exception as e:
            print("⚠️ Erreur pygame.event.get():", e)
            # On la repurge et on continue avec une liste vide
            pygame.event.pump()
            events = []

        for event in events:
            if event.type in [pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION, pygame.JOYHATMOTION]:
                game.gamepad_manager.handle_event(event)

            if event.type == pygame.QUIT:
                return "quitter"

            

            # Gestion des touches
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return options[selected].lower()
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)

            # Gestion des clics souris
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, opt in enumerate(options):
                    rect = pygame.Rect(
                        screen.get_width()//2 - font.size(opt)[0]//2,
                        250 + i*60,
                        font.size(opt)[0],
                        50
                    )
                    if rect.collidepoint(event.pos):
                        return opt.lower()

            # Gestion a la manette
            if event.type == pygame.JOYHATMOTION:
                x, y = event.value
                if y == 1:
                    selected = (selected - 1) % len(options)
                elif y == -1:
                    selected = (selected + 1) % len(options)

            if event.type == pygame.JOYBUTTONDOWN:
                try:
                    mapping = game.gamepad_manager.joystick_mappings.get(
+                        event.instance_id, BUTTON_MAP)
                    name = mapping.get(event.button, f"btn_{event.button}")                   

                    print(f"[MANETTE] Bouton pressé : {name}")
                    if name == "cross":
                        return options[selected].lower()

                except Exception as e:
                    print(f"[ERREUR] Bouton manette non traité : {e}")

def render_main_menu(screen, font, options, selected):
    """Affiche le menu principal."""
    screen.fill((30, 30, 70))
    title = pygame.font.Font(None, 74).render("L'univers d'Arielle", True, (255, 215, 0))
    screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
    for i, opt in enumerate(options):
        color = (0,255,0) if i == selected else (255,255,255)
        text = font.render(opt, True, color)
        screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 250 + i*60))
    pygame.display.flip()


if __name__ == '__main__':
    main()
