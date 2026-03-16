import pygame
import pickle
import os
from gamePad import BUTTON_MAP, GamepadManager

class LevelMenu:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        # Remplacer les polices par défaut
        try:
            # Essayez une police qui supporte les emojis (comme Segoe UI Emoji sur Windows)
            self.font = pygame.font.SysFont('segoe ui emoji', 25)
            self.title_font = pygame.font.SysFont('segoe ui emoji', 44)
        except pygame.error:
            # Fallback si la police emoji n'est pas disponible
            self.font = pygame.font.SysFont('arial', 30)
            self.title_font = pygame.font.SysFont('arial', 44)

        # Dans level_menu.py, modifiez la liste des niveaux dans __init__ :
        self.levels = [
            {
                "name": "Niveau 1", 
                "unlocked": True, 
                "image": "img/niveau1.png", 
                "completed": False,
                "win_condition": {
                    "type": "score_time", 
                    "score": 90,
                    "time": 25
                },
                "lose_condition": {
                    "health": 0,
                    "time": True
                }
            },
            {
                "name": "Niveau 2", 
                "unlocked": False, 
                "image": "img/niveau2.png", 
                "completed": False,
                "win_condition": {
                    "type": "reach_point", 
                    "point_name": "finish",
                    #"min_score": 30,
                    "time": 40
                },
                "lose_condition": {
                    "time": True,
                    #"min_score": 30
                },
                "wall_cost": 40
            },
            {
                "name": "Niveau 3", 
                "unlocked": False, 
                "image": "img/niveau3.png", 
                "completed": False,
                "win_condition": {
                    "type": "reach_point", 
                    "point_name": "finish",
                    "time": 150
                },
                "lose_condition": {
                    "time": True
                },
                "wall_cost": 40,
                "special_items": True
            },
            {
                "name": "Niveau 4", 
                "unlocked": False, 
                "image": "img/niveau4.png", 
                "completed": False,
                "win_condition": {
                    "type": "kill_all", 
                    "time": 130,
                    "boss_name": "final_boss"
                },
                "lose_condition": {
                    "time": True,
                    "health": 0
                },
                "bullet_upgrade": True
            }
        ]
        self.selected_index = 0
        self.thumb_size = (200, 150)
        self.load_progress()
        
        # Charger les miniatures
        for level in self.levels:
            try:
                level["thumbnail"] = pygame.transform.scale(
                    pygame.image.load(level["image"]).convert_alpha(),
                    self.thumb_size
                )
            except pygame.error:
                # Image par défaut si la miniature n'existe pas
                level["thumbnail"] = pygame.Surface(self.thumb_size)
                level["thumbnail"].fill((100, 100, 200) if level["unlocked"] else (50, 50, 50))

                # Ajouter le numéro du niveau
                text = self.font.render(level["name"][-1], True, (255, 255, 255))
                level["thumbnail"].blit(text, (
                    self.thumb_size[0]//2 - text.get_width()//2,
                    self.thumb_size[1]//2 - text.get_height()//2
                ))

    def load_progress(self):
        """Charge la progression depuis un fichier"""
        SAVE_FILE_PATH = 'saves/save.dat'
        try:
            # Créer le dossier saves s'il n'existe pas
            os.makedirs('saves', exist_ok=True)
            
            # Vérifier si le fichier existe
            if not os.path.exists(SAVE_FILE_PATH):
                # Créer une sauvegarde par défaut si le fichier n'existe pas
                self.levels[0]["unlocked"] = True  # Débloquer seulement le niveau 1
                self.save_progress()
                return
            
            with open(SAVE_FILE_PATH, 'rb') as f:
                data = pickle.load(f)
                # Vérification de l'intégrité des données
                if isinstance(data, list) and len(data) >= len(self.levels):
                    for i, level_data in enumerate(data[:len(self.levels)]):
                        if isinstance(level_data, dict):
                            self.levels[i]["unlocked"] = level_data.get("unlocked", False)
                            self.levels[i]["completed"] = level_data.get("completed", False)
        except (FileNotFoundError, EOFError, pickle.PickleError) as e:
            print(f"Erreur lors du chargement de la sauvegarde : {e}")
            # En cas d'erreur, réinitialiser avec le niveau 1 débloqué
            self.reset_progress()

    def save_progress(self):
        """Sauvegarde la progression dans un fichier"""
        try:
            SAVE_FILE_PATH = 'saves/save.dat'
            with open(SAVE_FILE_PATH, 'wb') as f:
                data = []
                for level in self.levels:
                    data.append({
                        "unlocked": level["unlocked"],
                        "completed": level["completed"]
                    })
                pickle.dump(data, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def unlock_level(self, level_num):
        """Déverrouille un niveau spécifique"""
        if 1 <= level_num <= len(self.levels):
            self.levels[level_num-1]["unlocked"] = True
            self.save_progress()

    def complete_level(self, level_num):
        """Marque un niveau comme complété et déverrouille le suivant"""
        if 1 <= level_num <= len(self.levels):
            self.levels[level_num-1]["completed"] = True
            if level_num < len(self.levels):
                self.levels[level_num]["unlocked"] = True
            self.save_progress()

    def draw(self):
        """Dessine l'écran de sélection des niveaux"""
        # Fond
        self.screen.fill((30, 30, 70))
        
        # Titre
        title_text = self.title_font.render("Sélection du Niveau", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen.get_width()//2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Paramètres de la grille
        cols = 2  # 2 colonnes
        thumb_width, thumb_height = self.thumb_size
        padding = 30  # Espacement entre les miniatures (augmenté de 20 à 30)
        margin_x = (self.screen.get_width() - (cols * (thumb_width + padding))) // 2
        margin_y = 150  # Marge depuis le haut
        
        # Affichage des niveaux en grille 2x2
        for i, level in enumerate(self.levels[:4]):  # Seulement les 4 premiers niveaux
            row = i // cols
            col = i % cols
            
            # Position calculée avec espacement
            x_pos = margin_x + col * (thumb_width + padding)
            y_pos = margin_y + row * (thumb_height + padding + 20)  # +20 pour espace vertical
            
            # Style de la bordure
            if not level["unlocked"]:
                default_border_color = (100, 100, 100)
            else:
                default_border_color = (200, 200, 200)
            border_color = (0, 255, 0) if i == self.selected_index else default_border_color
            border_width = 3 if i == self.selected_index else 2
            
            # Dessiner la bordure (rectangle légèrement plus grand que la miniature)
            pygame.draw.rect(self.screen, border_color, 
                            (x_pos - 5, y_pos - 5, thumb_width + 10, thumb_height + 10),
                            border_width)
            
            # Miniature avec effet si verrouillé
            thumb = level["thumbnail"].copy()
            if not level["unlocked"]:
                thumb.fill((100, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
                # Icône de verrou (texte ou image)
                lock_text = self.font.render("🔒", True, (255, 255, 255))
                thumb.blit(lock_text, (thumb_width//2 - lock_text.get_width()//2, 
                                    thumb_height//2 - lock_text.get_height()//2))
            elif level["completed"]:
                # Icône de validation
                check_text = self.font.render("✓", True, (0, 255, 0))
                thumb.blit(check_text, (thumb_width - 30, 10))
            
            # Afficher la miniature
            self.screen.blit(thumb, (x_pos, y_pos))
            
            # Nom du niveau sous la miniature
            name_text = self.font.render(level["name"], True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(x_pos + thumb_width//2, y_pos + thumb_height + 20))
            self.screen.blit(name_text, name_rect)
        
        # Instructions
        instr_text = self.font.render("← → ↑ ↓ pour sélectionner, ENTREE pour valider, Échap pour revenir", True, (200, 200, 200))
        instr_rect = instr_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height() - 50))
        self.screen.blit(instr_text, instr_rect)

    def reset_progress(self):
        """Réinitialise toute la progression des niveaux"""
        for i, level in enumerate(self.levels):
            level["completed"] = False
            level["unlocked"] = (i == 0)  # Seul le niveau 1 est débloqué
        self.save_progress()
        print("Progression réinitialisée.")



    def run(self):
        """Affiche et gère la sélection des niveaux."""
        clock = pygame.time.Clock()
        while True:
            self.draw()
            pygame.display.flip()

            

            
            for event in pygame.event.get():
                if event.type in [pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION, pygame.JOYHATMOTION]:
                    self.game.gamepad_manager.handle_event(event)

                # Quitter ou revenir au menu principal
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return "exit"

                # Sélection a la manette
                if event.type == pygame.JOYBUTTONDOWN :
                    mapping = self.game.gamepad_manager.joystick_mappings.get(
+                        event.instance_id, BUTTON_MAP)
                    name = mapping.get(event.button, f"btn_{event.button}")
                    if name == "cross":
                        if self.levels[self.selected_index]["unlocked"]:
                            return self.selected_index + 1

                    elif name == "circle":
                        return "exit"

                # Navigation au clavier
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.selected_index = max(0, self.selected_index - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_index = min(len(self.levels) - 1, self.selected_index + 1)
                    elif event.key == pygame.K_UP:
                        self.selected_index = max(0, self.selected_index - 2)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = min(len(self.levels) - 1, self.selected_index + 2)
                    elif event.key == pygame.K_RETURN:
                        if self.levels[self.selected_index]["unlocked"]:
                            return self.selected_index + 1
                    elif event.key == pygame.K_ESCAPE:
                        return "exit"

                # Sélection au clic
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cols = 2
                    w, h = self.thumb_size
                    padding = 30
                    margin_x = (self.screen.get_width() - (cols * (w + padding))) // 2 + padding // 2
                    margin_y = 150
                    for i, level in enumerate(self.levels[:4]):
                        row, col = divmod(i, cols)
                        x = margin_x + col * (w + padding)
                        y = margin_y + row * (h + padding + 20)
                        if pygame.Rect(x, y, w, h).collidepoint(event.pos) and level["unlocked"]:
                            return i + 1

                

            clock.tick(30)

    