import pygame
import pytmx
import pyscroll
import time
import random
from player import Player
from typing import Optional
from collectible import Collectible, SpecialCollectible
from monster import Monster
from particle import Particle
from gamePad import GamepadManager
from destructibleWall import DestructibleWall
from summaries import LEVEL_SUMMARIES, GAME_INTRODUCTION


class Game:
  def __init__(self, screen):
    self.menu_context = "in_game"
    self.pause_selected_index = 0
    self.pause_menu_options = []
    
    # Configuration de base
    self.screen = screen
    self.clock = pygame.time.Clock()


    # Initialisation de Pygame Mixer
    pygame.mixer.init()

    # Initialisation des attributs avant utilisation
    self.tmx_data = None
    self.map_data = None
    self.map_layer = None
    self.level_menu = None
    self.options_menu = None
    self.group = None
    self.collectibles = pygame.sprite.Group()
    self.monsters = pygame.sprite.Group()
    self.particles = pygame.sprite.Group()
    
    # Polices
    self.title_font = pygame.font.Font(None, 74)
    self.menu_font = pygame.font.Font(None, 50)
    self.score_font = pygame.font.Font(None, 36)

    self.destructible_walls = pygame.sprite.Group()  # Nouveau groupe pour les murs destructibles
    self.walls_to_destroy_after_monster = pygame.sprite.Group()  # Murs à détruire après monstre

    # État du jeu
    
    self.score = 0
    self.start_time = 0
    self.time_limit = 60  # 60 secondes par défaut
  
    self.music_volume = 0.5  # Valeurs par défaut
    self.sfx_volume = 0.5


    # Charger le son
    #sound_effect = pygame.mixer.Sound('sound_effect.wav')
    self.level_up_sound = pygame.mixer.Sound("song/power_up.wav") 
    self.level_up_sound.set_volume(self.sfx_volume)
    
    # Menu d'options
    
    self.current_level = 1
    self.player = None
    # Pour la gestion des messages de collision avec un mur
    self.collision_message     = ""
    self.message_start_time    = 0       # timestamp du début d'affichage du message
    self.message_duration      = 2000    # durée d'affichage en ms
    self.current_message       = ""
    self.message_timer         = 0.0
    # Pour la destruction dynamique : 1er mur 40 pts, puis +20 à chaque fois
    self.destroyed_wall_count  = 0
    self.destroy_cost_increment = 20

    # Collision pour murs fixes (impassables)
    self.static_collision_rects = []
    # Collision pour murs destructibles (déclenchée dans handle_destructible_walls)
    self.destructible_collision_rects = []
    # Nouveaux pièges (rects)
    self.trap_rects = []

    # Statuts liés aux pièges
    self.trap_immunity = False
    self.trap_immunity_timer = 0.0         # en secondes
    self.score_multiplier = 1              # multiplicateur pour les pièces
    self.piece_multiplier_timer = 0.0      # durée restante du doublement
    self.time_multiplier = 1.0  

    self.current_room = 1

    self.gamepad_manager = GamepadManager(self)

  def show_message(self, text: str, duration: float):
    """
    Affiche `text` pendant `duration` secondes à l'écran.
    """
    self.current_message = text
    self.message_timer   = duration

  def show_level_intro(self):
    """Affiche le résumé du niveau courant jusqu’à appui d’une touche."""
    summary = LEVEL_SUMMARIES[self.current_level]
    lines = summary.split("\n")
    intro_active = True
    while intro_active:
      for event in pygame.event.get():
        if event.type in (pygame.KEYDOWN, pygame.JOYBUTTONDOWN):
          intro_active = False

      self.screen.fill((30, 30, 70))
      for i, line in enumerate(lines):
        surf = self.menu_font.render(line, True, (255, 255, 255))
        rect = surf.get_rect(center=(self.screen.get_width() // 2, 150 + i * 50))
        self.screen.blit(surf, rect)

      pygame.display.flip()
      self.clock.tick(30)
  
  def show_game_intro(self):
    """Affiche l'introduction générale au lancement du jeu"""
    intro_lines = GAME_INTRODUCTION.split("\n")
    intro_active = True
    
    while intro_active:
        for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.JOYBUTTONDOWN, pygame.MOUSEBUTTONDOWN):
                intro_active = False

        self.screen.fill((30, 30, 70))  # Fond bleu foncé
        y_offset = 100
        for line in intro_lines:
            text_surface = self.menu_font.render(line.strip('*'), True, (255, 255, 255))
            rect = text_surface.get_rect(center=(self.screen.get_width()//2, y_offset))
            self.screen.blit(text_surface, rect)
            y_offset += 40

        # Ajout d'une indication pour continuer
        prompt = self.score_font.render("Appuyez sur n'importe quel bouton pour continuer...", True, (200, 200, 200))
        prompt_rect = prompt.get_rect(center=(self.screen.get_width()//2, self.screen.get_height() - 50))
        self.screen.blit(prompt, prompt_rect)
        
        pygame.display.flip()
        self.clock.tick(30)

  def load_game_resources(self):
    """Charge les ressources persistantes"""
    try:
        self.load_map_data()
        self.convert_numeric_properties()
        self.initialize_map_layer()
    except Exception as e:
        print(f"Erreur lors du chargement de la carte : {e}")
        raise SystemExit("Impossible de charger les ressources du jeu")
    self.group = pyscroll.PyscrollGroup(self.map_layer, default_layer=5)

  def load_map_data(self):
    """Charge les données de la carte"""
    level_map = f"maps/niveau{self.current_level}.tmx"
    print(f"[DEBUG] Chargement de la carte : {level_map}")
    
    self.tmx_data = pytmx.util_pygame.load_pygame(level_map)

  def convert_numeric_properties(self):
    """Convertit les propriétés numériques des objets de la carte"""
    for obj in self.tmx_data.objects:
        if hasattr(obj, 'properties'):
            for key, value in obj.properties.items():
                if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                    obj.properties[key] = self.convert_to_number(value)

  def convert_to_number(self, value):
    """Convertit une chaîne en nombre (int ou float) si possible"""
    try:
        float_val = float(value)
        return int(float_val) if float_val.is_integer() else float_val
    except ValueError:
        return value

  def initialize_map_layer(self):
    """Initialise le calque de la carte"""
    self.map_data = pyscroll.data.TiledMapData(self.tmx_data)
    self.map_layer = pyscroll.orthographic.BufferedRenderer(self.map_data, self.screen.get_size())
    if self.current_level == 4:
      self.map_layer.zoom = 0.6
    else :
      self.map_layer.zoom = 0.8

    
  def initialize_game_state(self):
    """Réinitialise l'état du jeu pour une nouvelle partie"""
    self.score = 0
    self.reset_game_state()
    self.setup_collision_rects()
    self.setup_player()
    self.setup_collectibles()
    self.setup_monsters()
    self.setup_level_conditions()
    self.destroyed_wall_count = 0
    self.setup_destructible_walls()
    self.setup_special_items()
    self.group.update()
    self.group.center(self.player.rect.center)

  def reset_game_state(self):
    """Réinitialise les groupes et ressources du jeu."""
    self.load_game_resources()
    self.collectibles.empty()
    self.monsters.empty()
    self.particles.empty()
    self.group.empty()
    self.group = pyscroll.PyscrollGroup(self.map_layer, default_layer=5)

  def setup_player(self):
    """Initialise le joueur."""
    player_spawn = self.tmx_data.get_object_by_name("player")
    print(f"[DEBUG] player_spawn = {player_spawn}")
    if not player_spawn:
        raise ValueError("Erreur : aucun point de spawn 'player' trouvé dans la carte TMX.")

    if self.player is None:
      self.player = Player(player_spawn)
    else:
      self.player.rect.topleft = (player_spawn.x, player_spawn.y)
    
    if self.current_level == 4:
      self.player.health = 1000
    else :
      self.player.health = 100

    self.group.add(self.player)

  def setup_collectibles(self):
    """Ajoute les collectibles à la carte."""
    for obj in self.tmx_data.objects:
      if obj.name == "collectible":
        item = Collectible(obj.x, obj.y, 'img/coin.png')
        if hasattr(obj, 'score_value'):
            item.value = int(obj.score_value)
        self.collectibles.add(item)
      
      elif obj.name == "special_item" or obj.type == "special_item":
        print(obj)
        effect_type = obj.properties.get("effect", "score")
        effect_value = int(obj.properties.get("value", 25))
        item = SpecialCollectible(obj.x, obj.y, 'img/special_coin.png', effect_type, effect_value)
        self.collectibles.add(item)
        self.group.add(item)
    self.group.add(self.collectibles)

  def setup_monsters(self):
    """Ajoute les monstres à la carte et les rend actifs immédiatement."""
    # 1) Combinez tous vos rectangles de collision (fixes + destructibles)
    collision_list = self.static_collision_rects + self.destructible_collision_rects

    # 2) Videz l'ancien groupe au cas où (rechargement de niveau, etc.)
    self.monsters.empty()
    
    # 3) Pour chaque objet "monster" dans votre TMX, créez-le correctement une seule fois
    for obj in self.tmx_data.objects:
        if obj.name == "monster":
          group = obj.properties.get("group", "salle1")
          if self.current_level != 4 or group == "salle1":
            zone_name = f"{group}_zone"
            zone_obj = self.tmx_data.get_object_by_name(zone_name) if zone_name in self.tmx_data.objects_by_name else None
            zone_rect = pygame.Rect(zone_obj.x, zone_obj.y, zone_obj.width, zone_obj.height) if zone_obj else None

            monster = Monster(obj, collision_list, self.player, zone_rect=zone_rect)
            monster.group = group
            monster.map_width = self.tmx_data.width * self.tmx_data.tilewidth
            monster.map_height = self.tmx_data.height * self.tmx_data.tileheight
            self.monsters.add(monster)


    # 4) **Très important** : dites à pyscroll de dessiner le groupe de monstres
    self.group.add(self.monsters)

  def setup_level_conditions(self):
    """Configure les conditions spécifiques au niveau."""
    if self.level_menu and 0 < self.current_level <= len(self.level_menu.levels):
        level_info = self.level_menu.levels[self.current_level - 1]

        # Sauvegarde en attribu pour isolation
        self.lose_condition = level_info.get("lose_condition", {})
        self.win_condition = level_info.get("win_condition", {})

        # Temps imparti
        self.time_limit = self.win_condition.get("time", 60)
        # Coût des murs destructibles
        self.wall_cost = level_info.get("wall_cost", 40)
        
  def setup_destructible_walls(self):
    """Ajoute les murs destructibles avec coûts par palier."""
    for obj in self.tmx_data.objects:      
      if obj.name == "destructible_wall":
          wall = DestructibleWall(obj.x, obj.y, obj.width, obj.height)
          print(wall)
          self.destructible_walls.add(wall)
          self.group.add(wall)
          # On conserve aussi son rect pour la détection spécifique
          self.destructible_collision_rects.append(wall.rect)
      if obj.name == "wall_after_monster":
          wall = DestructibleWall(obj.x, obj.y, obj.width, obj.height, requires_monster=True)
          self.walls_to_destroy_after_monster.add(wall)
          self.group.add(wall)

  def setup_special_items(self):
    """Ajoute les items spéciaux pour certains niveaux."""
    if self.current_level == 3:
        for obj in self.tmx_data.objects:
            if obj.name == "special_item" or obj.type == "special_item":
              print(obj)
              effect_type = obj.properties.get("effect", "score")
              effect_value = int(obj.properties.get("value", 25))
              item = SpecialCollectible(obj.x, obj.y, 'img/special_coin.png', effect_type, effect_value)
              self.collectibles.add(item)
              self.group.add(item)

  def setup_collision_rects(self):
    """Configure les rectangles de collision (murs fixes et destructibles)."""
    self.static_collision_rects  = []
    self.destructible_collision_rects = []
    self.trap_rects = []

    for obj in self.tmx_data.objects:
      
      # Inclut les zones de collision classiques et tous les murs TMX
      if obj.name == "collision":
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        self.static_collision_rects.append(rect)

      if obj.name == "destructible_wall":
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        self.destructible_collision_rects.append(rect)

      if obj.name == "piege":
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        self.trap_rects.append(rect)

    # Liste unifier
    self.collision_rects = (self.static_collision_rects + self.destructible_collision_rects)

  def apply_random_trap_effect(self):
    """Choisit un effet aléatoire et l’applique au joueur."""
    
    effects = [
        "life", "score", "time_accel", "time_slow", 
        "player_slow", "player_fast", "teleport",
        "double_pieces", "immunity"
    ]
    effect = random.choice(effects)
    # Appliquer
    if effect == "life":
        self.player.health = max(0, self.player.health - 20)
        print(f"Effet appliqué: {self.player.health} points de vie")
    
    elif effect == "score":
        self.score = max(0, self.score - 15)
        print(f"Effet appliqué: {self.score} points")
    
    elif effect == "time_accel":
        # On fait comme si 50% du temps restant est déjà passé
        self.time_multiplier *= 4
        print(f"Effet appliqué: acceleration {self.time_multiplier} x vitesse")
    
    elif effect == "time_slow":
        # ralentit le temps (moitié moins vite)
        self.time_multiplier *= 0.5
        print(f"Effet appliqué: ralentissement {self.time_multiplier} x vitesse")
    
    elif effect == "player_slow":
      # On redonne 50% du temps écoulé
        self.player.speed = self.player.speed - random.randint(-1, 4)
        print(f"Effet appliqué: {self.player.speed} vitesse du joueur ralenti")
    
    elif effect == "player_fast":
        self.player.speed = self.player.speed + random.randint(-1, 4)
        print(f"Effet appliqué: {self.player.speed} vitesse du joueur accelere")
    elif effect == "teleport":
        self.teleport_player_randomly()
        print(f"Effet appliqué: {self.player.rect} position du joueur")
    
    elif effect == "double_pieces":
        self.score_multiplier = 2
        self.piece_multiplier_timer = 5.0
    
    elif effect == "immunity":
        self.trap_immunity = True
        self.trap_immunity_timer = 5.0
    # Vous pouvez afficher un feedback visuel / sonore ici
    print(f"Effet appliqué: {effect}")
    return effect

  def teleport_player_randomly(self):
    """
    Téléporte le joueur aléatoirement en Avant ou en Arrière
    sur son parcours (même ligne Y), sans sortir de la carte.
    """
    # Coordonnées actuelles
    cur_x, cur_y = self.player.rect.topleft

    # largeur totale de la carte en pixels
    map_width = self.tmx_data.width * self.tmx_data.tilewidth

    # on se déplace de -5 à +5 tiles
    max_off_pixels = 50 * self.tmx_data.tilewidth
    offset = random.randint(-max_off_pixels, max_off_pixels)

    new_x = cur_x + offset
    # clamp pour rester dans la carte
    new_x = max(0, min(new_x, map_width - self.player.rect.width))

    self.player.rect.x = new_x
    # Y inchangé pour rester “sur le parcours”
    self.player.rect.y = cur_y

  def game_over_screen(self, reason):
    """Affiche brièvement l'écran de défaite et retourne au menu niveau."""

    self.screen.fill((30, 30, 70))
    game_over_font = pygame.font.Font(None, 74)
    game_over_text = game_over_font.render("Défaite!", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/2 - 20))

    reason_font = pygame.font.Font(None, 36)
    reason_msg = f"Défaite: {reason}. Retour au menu dans 3 secondes..."
    reason_text = reason_font.render(reason_msg, True, (255, 255, 255))
    reason_rect = reason_text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/2 + 40))

    self.screen.blit(game_over_text, game_over_rect)
    self.screen.blit(reason_text, reason_rect)
    pygame.display.flip()
    pygame.time.delay(3000)

    # Réinitialiser l'état du jeu pour un nouveau départ
    self.reset_game_state()

    return False  # ➔ Retour immédiat au menu de sélection de niveaux

  def get_remaining_time(self) -> float:
    """Retourne le temps restant, sans déclencher la fin de partie."""
    elapsed = time.time() - self.start_time
    return max(0.0, self.time_limit - elapsed)

  def win(self, reason):
    win_font = pygame.font.Font(None, 74)
    win_text = win_font.render("Victoire !", True, (0, 255, 0))
    win_rect = win_text.get_rect(center=(self.screen.get_width() / 2, 100))

    info_font = pygame.font.Font(None, 36)
    info_msg = f"Victoire: {reason}. Retour au menu dans 3 secondes..."
    info_text = info_font.render(info_msg, True, (255, 255, 255))
    info_rect = info_text.get_rect(center=(self.screen.get_width() / 2, 180))

    self.screen.fill((30, 30, 70))
    self.screen.blit(win_text, win_rect)
    self.screen.blit(info_text, info_rect)
    pygame.display.flip()
    # Pause de 3 secondes avant retour automatique au menu
    pygame.time.delay(3000)

    #waiting = True
    #while waiting:
    #    for event in pygame.event.get():
    #        if event.type == pygame.QUIT:
    #            pygame.quit()
    #            exit()
    #        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
    #            waiting = False

    # Enregistrement progression
    if self.level_menu:
      self.level_menu.complete_level(self.current_level)

    # Réinitialiser l'état du jeu pour un nouveau départ
    self.reset_game_state()

    return True  # retour au menu des niveaux
  
  def check_end_conditions(self) -> Optional[bool]:
    """
    Vérifie si l'on doit terminer la partie.
    Retourne False pour défaite, True pour victoire, ou None pour continuer.
    """
    # Niveau 3 : collision piège applique un effet aléatoire (si pas immunisé)
    if self.current_level == 3:
      for trap in self.trap_rects:
        if (self.player.rect.colliderect(trap) and not self.trap_immunity):
          self.apply_random_trap_effect()
          # petit cooldown pour ne pas réappliquer dans la même frame
          self.trap_immunity = True
          self.trap_immunity_timer = 0.5
          break


    elapsed = time.time() - self.start_time
    # Récupérer les conditions de fin (défaite/victoire) du niveau courant
    lose = getattr(self, "lose_condition", {})
    win  = getattr(self, "win_condition", {})
    
    # Condition de défaite
    if self.player.health <= 0:
        return self.end_game(False, "Vie épuisée")
    if lose.get("time") and elapsed >= self.time_limit:
        return self.end_game(False, "Temps écoulé")
    if lose.get("min_score") and self.score < lose["min_score"]:
        return self.end_game(False, "Score insuffisant")
    
    # Condition de victoire
    if win["type"] == "score_time" and self.score >= win["score"]:
        return self.end_game(True, "Score atteint")
    if win["type"] == "reach_point" and self.check_reach_point_condition(win):
        return self.end_game(True, "Arrivé au point")
    if win["type"] == "kill_all" :
      # Ne valider kill_all qu’une fois la salle 2 activée et vidée
      if not (self.current_level == 4 and self.current_room == 1):
          if self.check_kill_all_condition(win):
              return self.end_game(True, "Tous les ennemis vaincus")
    
    return None

  def check_reach_point_condition(self, win: dict) -> bool:
    """
    Vérifie si le joueur a atteint le point nommé (e.g. 'finish').
    """
    point_name = win.get("point_name")
    if not point_name:
      return False
    obj = self.tmx_data.get_object_by_name(point_name)
    if not obj:
      return False
    # Crée un rectangle à partir de l'objet TMX et teste la collision
    rect = pygame.Rect(obj.x, obj.y, getattr(obj, "width", 0), getattr(obj, "height", 0))
    return self.player.rect.colliderect(rect)

  def check_kill_all_condition(self, win: dict) -> bool:
    """
    Vérifie si tous les monstres ont été vaincus.
    """
    # Si la condition comporte un boss_name, on pourrait filtrer,
    # mais ici on considère simplement qu'il ne reste plus de monstres.
    return len(self.monsters) == 0

  def pause_menu(self):
    """Affiche le menu pause et retourne True pour Menu principal, False pour Reprendre."""
    options = self.create_pause_menu_options()
    selected_index = 0

    while True:
        # Affichage
        self.render_pause_menu(options, selected_index)

        # Événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Navigation clavier
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # reprendre
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    action = options[selected_index]["action"]
                    if action == "resume":
                        return False
                    elif action == "main_menu":
                        return True
                    elif action == "options":
                        self.options_menu.run(self)
                    elif action == "quit":
                        pygame.quit()
                        exit()

            # Souris
            elif event.type == pygame.MOUSEMOTION:
                for i, opt in enumerate(options):
                    if opt["rect"].collidepoint(event.pos):
                        selected_index = i
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, opt in enumerate(options):
                    if opt["rect"].collidepoint(event.pos):
                        action = opt["action"]
                        if action == "resume":
                            return False
                        elif action == "main_menu":
                            return True
                        elif action == "options":
                            self.options_menu.run(self)
                        elif action == "quit":
                            pygame.quit()
                            exit()

            # Manette : croix directionnelle (hat)
            elif event.type == pygame.JOYHATMOTION:
                x, y = event.value
                if y == 1:
                    selected_index = (selected_index - 1) % len(options)
                elif y == -1:
                    selected_index = (selected_index + 1) % len(options)

            # Manette : boutons
            elif event.type == pygame.JOYBUTTONDOWN:
                # 2 = Croix (X) sur PS4 ; à adapter selon votre mapping
                if event.button == 2:
                    action = options[selected_index]["action"]
                    if action == "resume":
                        return False
                    elif action == "main_menu":
                        return True
                    elif action == "options":
                        self.options_menu.run(self)
                    elif action == "quit":
                        pygame.quit()
                        exit()

                if event.button == 1:
                    return False

  def create_pause_menu_options(self):
    """Crée les options du menu pause."""
    self.pause_menu_options = [
      {"text": "Reprendre", "action": "resume"},
      {"text": "Options", "action": "options"},
      {"text": "Menu principal", "action": "main_menu"},
      {"text": "Quitter", "action": "quit"}
    ]

    return self.pause_menu_options

  def render_pause_menu(self, options, selected_index):
    """Affiche le menu pause à l'écran."""
    self.screen.fill((30, 30, 70))
    title_text = self.title_font.render("Pause", True, (255, 215, 0))
    title_rect = title_text.get_rect(center=(self.screen.get_width() / 2, 100))
    self.screen.blit(title_text, title_rect)

    for i, option in enumerate(options):
      color = (0, 255, 0) if i == selected_index else (255, 255, 255)
      text = self.menu_font.render(option["text"], True, color)
      text_rect = text.get_rect(center=(self.screen.get_width() / 2, 200 + i * 60))
      option["rect"] = text_rect
      self.screen.blit(text, text_rect)

    pygame.display.flip()

  def handle_pause_menu_keydown(self, event, options, selected_index):
    """Gère les événements clavier dans le menu pause."""
    if event.key == pygame.K_ESCAPE:
      return False
    if event.key == pygame.K_UP:
      return (selected_index - 1) % len(options)
    if event.key == pygame.K_DOWN:
      return (selected_index + 1) % len(options)
    if event.key == pygame.K_RETURN:
      return self.execute_pause_menu_action(options[selected_index]["action"])
    return selected_index

  def handle_pause_menu_mousemotion(self, event, options, selected_index):
    """Gère le survol de la souris dans le menu pause."""
    for i, option in enumerate(options):
      if option["rect"].collidepoint(event.pos):
        return i
    return selected_index

  def handle_pause_menu_mouseclick(self, event, options, selected_index):
    """Gère les clics de souris dans le menu pause."""
    for i, option in enumerate(options):
      if option["rect"].collidepoint(event.pos):
        return self.execute_pause_menu_action(option["action"])
    return True, selected_index

  def execute_pause_menu_action(self, action):
    """Exécute l'action sélectionnée dans le menu pause."""
    if action == "resume":
      return False
    elif action == "options":
      self.options_menu.run(self)
    elif action == "main_menu":
      return True
    elif action == "quit":
      pygame.quit()
      exit()
    return True

  def run(self):
    """Boucle principale du jeu"""
    while True:
      self.initialize_game_state()
      self.game_loop()
      
  def game_loop(self) -> bool:
    """Boucle de jeu principale, retourne True si victoire, False si défaite."""
    self.start_time = time.time()
    clock = pygame.time.Clock()

    self.show_level_intro()

    while True:


      # 1. Calcul du dt en tenant compte de time_multiplier  # <<< CHANGÉ
      raw_dt = clock.tick(60) / 1000.0
      dt = raw_dt * self.time_multiplier



      # Mettre à jour message éphémère
      if self.message_timer > 0:
        self.message_timer -= dt
        if self.message_timer <= 0:
          self.current_message = ""

      # 2. Mise à jour des timers
      if self.trap_immunity_timer > 0:
        self.trap_immunity_timer -= dt
        if self.trap_immunity_timer <= 0:
          self.trap_immunity = False

      if self.piece_multiplier_timer > 0:
        self.piece_multiplier_timer -= dt
        if self.piece_multiplier_timer <= 0:
          self.score_multiplier = 1
        
      # 3. Traitement des entrées & update logique
      pygame.event.pump()
      if not self.handle_events(clock):
        return False  # permet de quitter via pause menu
      self.handle_input()
      # Animer tous les sprites (player, monstres, etc.)
      self.group.update()
      self.update_game_state()  # collectibles, monsters, particules…
      
      # 4. Détection pièges (niveau 3) + suppression du piège  # <<< CHANGÉ
      if self.current_level == 3 and not self.trap_immunity:
        for trap in self.trap_rects[:]:            # on parcourt une copie
          if self.player.rect.colliderect(trap):
            effect = self.apply_random_trap_effect()
            # Afficher un message selon l'effet
            self.show_message(f"Effet piège : {effect}", 2.0)
            self.trap_rects.remove(trap)        # le piège ne réapparaît plus
            self.trap_immunity = True
            self.trap_immunity_timer = 0.5
            break

      # 2. Vérification fin de partie
      result = self.check_end_conditions()
      if result is not None:
          return result

      # 3. Affichage
      self.render_game()
      clock.tick(60)

  def update_game_state(self):
    """Met à jour l'état du jeu."""
    #self.handle_input()
    self.check_collectible()
    self.check_monster_collision()
    self.particles.update()
    self.player.bullets.update()
    self.check_bullet_wall_collision()
    self.group.add(*self.player.bullets)
    self.check_bullet_monster_collision()
    self.monsters.update()
    self.group.center(self.player.rect.center)

    # 🔫 Tir continu clavier
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] or keys[pygame.K_f]:
        self.player.shoot()

    # ✅ Tir avec manette (bouton "cross" détecté par GamepadManager)
    if self.gamepad_manager:
        for joystick in self.gamepad_manager.joysticks:
            if joystick.get_button(0):  # Bouton "cross" ou équivalent
                self.player.shoot()



  def check_bullet_monster_collision(self):
    """Vérifie si une balle touche un monstre et applique les dégâts."""
    for bullet in self.player.bullets:
      hits = pygame.sprite.spritecollide(bullet, self.monsters, False)
      for monster in hits:
        # 1) On applique les dégâts au monstre
        monster.take_damage(bullet.power)
        # 2) On détruit la balle
        bullet.kill()
        # 3) On crée l’effet d’impact
        self.create_impact_effect(monster.rect.center)
        # 4) Si le monstre est mort, on déclenche l’effet de collecte
        if not monster.alive():
          self.create_collect_effect(monster.rect.center)          

          # Déclencher la salle 2 si tous les monstres de salle1 sont morts
          # Si on vient de tuer le dernier monstre de la salle1 → on active salle2
          if self.current_level == 4 and self.current_room ==1 and not any(m.group == "salle1" for m in self.monsters):
            self.current_room = 2
            self.activate_monsters("salle2")
            self.show_message("Salle 2 activée !", 2.0)

  def check_bullet_wall_collision(self):
    """Vérifie si une balle heurte un mur (statique ou destructible)."""
    # On itère sur une copie car on peut tuer des balles en cours de boucle
    for bullet in list(self.player.bullets):
        for wall_rect in self.collision_rects:
            if bullet.rect.colliderect(wall_rect):
                # Effet d’impact
                self.create_impact_effect(bullet.rect.center)
                # On enlève la balle
                bullet.kill()
                # Une seule collision suffit
                break



  def render_game(self):
    """Rend le jeu à l'écran."""
    self.screen.fill((0, 0, 0))
    self.group.draw(self.screen)
    self.particles.draw(self.screen)
    self.player.bullets.draw(self.screen)
    for monster in self.monsters:
      monster.draw_effects(self.screen)
      monster.draw_health_bar(self.screen)

    self.draw_score()
    if self.current_level == 4:
        self.draw_boss_health()
    
    # 3) HUD : nombre de monstres restants par salle
    if self.current_room == 1:
        count = sum(1 for m in self.monsters if getattr(m, "group", "salle1") == "salle1")
        txt = self.score_font.render(f"Salle 1 : {count}", True, (255,255,255))
    elif self.current_room == 2:
        count = sum(1 for m in self.monsters if getattr(m, "group", None)      == "salle2")
        txt = self.score_font.render(f"Salle 2 : {count}", True, (255,255,255))
    self.screen.blit(txt, (150, 10))

    pygame.display.flip()

  def handle_events(self, clock):
    """Gère les événements du jeu."""
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        exit()
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          if self.pause_menu():
            return False  # Retour au menu sans débloquer de niveau
        elif event.key == pygame.K_f:
          if self.player:
            self.player.shoot()

      else:
        self.gamepad_manager.handle_event(event)  # Gère aussi manette
        
    clock.tick(60)
    return True

  def handle_button_down(self, name):
    if name == "cross":
        if self.player:
            self.player.shoot()
    elif name == "circle":
        if self.player and hasattr(self.player, "dash"):
            self.player.dash()
            print("[MANETTE] dash() appelé")
    elif name == "start" or name == "options":
        self.pause_menu()
    else:
        print(f"[MANETTE] Bouton pressé : {name}")

  def handle_button_up(self, name):
      pass  # Si besoin

  def handle_axis_motion(self, axis, val):
    print(f"[DEBUG] AXIS {axis} = {val}")
    # Si on est dans un menu, ignorer joystick_axis
    if self.player is None or not hasattr(self.player, 'joystick_axis'):
      return

    if self.player is not None:
      if axis == "left_x":
        self.player.joystick_axis[0] = val
      elif axis == "left_y":
        self.player.joystick_axis[1] = val

  def handle_dpad(self, value):
    x, y = value
    print(f"[DPAD] value = {value}")  # pour debug

    if self.menu_context in ["start_menu", "pause_menu", "level_menu"]:
        if self.menu_context == "level_menu":
          if x == 1:
              self.level_menu.selected_index = min(len(self.level_menu.levels) - 1, self.level_menu.selected_index + 1)
          elif x == -1:
              self.level_menu.selected_index = max(0, self.level_menu.selected_index - 1)
          elif y == -1:
              self.level_menu.selected_index = min(len(self.level_menu.levels) - 1, self.level_menu.selected_index + 2)
          elif y == 1:
              self.level_menu.selected_index = max(0, self.level_menu.selected_index - 2)
        else:
            if y == 1:
                self.navigate_menu("up")
            elif y == -1:
                self.navigate_menu("down")
            elif x == 1:
                self.navigate_menu("right")
            elif x == -1:
                self.navigate_menu("left")
    else:
        if self.player is not None:
          self.player.joystick_axis = [float(x), float(-y)]

  def draw_score(self):
    # Créer le texte du score
    text_surface = self.score_font.render(f"Score: {self.score}", True, (255, 255, 255))
    border_surface = self.score_font.render(f"Score: {self.score}", True, (0, 0, 0))

    

    # Dessiner la bordure
    offsets = [(-1,-1), (-1,1), (1,-1), (1,1)]
    for dx, dy in offsets:
        self.screen.blit(border_surface, (10 + dx, 10 + dy))    
    self.screen.blit(text_surface, (10, 10))

    # Santé
    health_text = f"Vie: {self.player.health}"
    health_surface = self.score_font.render(health_text, True, (255, 0, 0))
    self.screen.blit(health_surface, (10, 50))

    # chrono
    remaining_time = self.get_remaining_time()
    time_text_str = f"Temps: {int(remaining_time)}s"
    time_text = self.score_font.render(time_text_str, True, (255, 255, 255))
    time_border = self.score_font.render(time_text_str, True, (0, 0, 0))

    # Position en haut à droite
    time_pos = (self.screen.get_width() - time_text.get_width() - 10, 10)
    for dx, dy in offsets:
        self.screen.blit(time_border, (time_pos[0] + dx, time_pos[1] + dy))
    self.screen.blit(time_text, time_pos)

    # Afficher le message de collision si actif
    now = pygame.time.get_ticks()
    if self.collision_message and now - self.message_start_time < self.message_duration:
      msg_surf = self.score_font.render(self.collision_message, True, (255, 215, 0))
      msg_rect = msg_surf.get_rect(center=(self.screen.get_width()/2, 50))
      self.screen.blit(msg_surf, msg_rect)

    # Affichage du message éphémère (si actif)
    if self.current_message:
      surf = self.score_font.render(self.current_message, True, (255, 255, 255))
      # positionnez-le où vous voulez, ici, centré en haut
      rect = surf.get_rect(center=(self.screen.get_width()//2, 50))
      # On peut dessiner un fond semi-transparent
      bg = pygame.Surface((rect.w+20, rect.h+10), pygame.SRCALPHA)
      bg.fill((0, 0, 0, 150))  # noir à 60% d'opacité
      bg_rect = bg.get_rect(center=rect.center)
      self.screen.blit(bg, bg_rect)
      self.screen.blit(surf, rect)
    
  def check_collectible(self):
    
    # Détecter les collisions joueur/objects
    collisions = pygame.sprite.spritecollide(self.player, self.collectibles, True)      
    for item in collisions:
        if isinstance(item, SpecialCollectible):
            self.apply_special_effect(item)
        else:
            self.score += item.value * self.score_multiplier
        
        self.create_collect_effect(item.rect.center, is_wall=False)
    
  def apply_special_effect(self, item):
    if item.effect_type == "speed":
        self.player.speed += item.effect_value
    elif item.effect_type == "jump":
        self.player.has_double_jump = True
    elif item.effect_type == "time":
        self.start_time += item.effect_value  # Ajoute ou retire du temps
    elif item.effect_type == "bullet":
        self.player.bullet_power += item.effect_value
    # 'score' est déjà géré par la classe parente

  def load_boss_room(self):
    # Charger la salle du boss
    boss_info = self.special_points["final_boss"]
    boss = Monster(boss_info, self.collision_rects, self.player)
    boss.is_boss = True
    boss.health = 100
    self.monsters.add(boss)
    
    # Ajuster la musique et l'ambiance
    pygame.mixer.music.load("song/boss_music.ogg")
    pygame.mixer.music.play()
    
    # Réinitialiser le timer pour la phase de boss
    self.start_time = time.time()
    self.time_limit = 30  # 30 secondes pour battre le boss

  def draw_boss_health(self):
    """Affiche une barre de vie pour le boss s’il existe"""
    boss = next((m for m in self.monsters if hasattr(m, "is_boss") and m.is_boss), None)
    if not boss:
        return
    # Barre de vie basique
    bar_width = 300
    bar_height = 20
    x = (self.screen.get_width() - bar_width) // 2
    y = 80

    # Calcul de la largeur remplie
    health_ratio = boss.health / 100
    filled = int(bar_width * health_ratio)

    # Fond
    pygame.draw.rect(self.screen, (100, 0, 0), (x, y, bar_width, bar_height))
    # Barre
    pygame.draw.rect(self.screen, (255, 0, 0), (x, y, filled, bar_height))


  def create_collect_effect(self, pos, is_wall=False):
    # Système de particules simple
    for _ in range(15 if is_wall else 10):  # Plus de particules pour les murs
      color = (150, 75, 0) if is_wall else (255, 215, 0)  # Marron pour les murs
      self.particles.add(Particle(pos, color))

  def create_impact_effect(self, pos):
    for _ in range(5):
        self.particles.add(Particle(pos, (255, 100, 0)))  # effet rouge/orange


  def check_monster_collision(self):  # Nouvelle méthode
    collided_monsters = pygame.sprite.spritecollide(self.player, self.monsters, False)
    for monster in collided_monsters:
      monster.reset_position()  # Réinitialise chaque monstre en collision
      monster.increase_detection(self.level_up_sound)  # Augmente la portée de détection (self.level_up_sound)
      
      # Réduire la vie
      damage = 20 if self.score > 20 else 40
      self.player.health -= damage

      # Empêcher la vie négative
      self.player.health = max(0, self.player.health)

      if self.player.health <= 0:
        self.player.health = 0
         

      print("Monstre déplacé aléatoirement!")

      



    # Vérifier si tous les monstres sont vaincus pour détruire certains murs
    if len(self.monsters) == 0:
        for wall in self.walls_to_destroy_after_monster:
            wall.destroy()
            # Ajouter des effets visuels
            self.create_collect_effect(wall.rect.center, is_wall=True)
    
  def check_collision(self, proposed_rect):
    return any(proposed_rect.colliderect(rect) for rect in self.collision_rects)

  def activate_monsters(self, group_name):
    collision_list = self.static_collision_rects + self.destructible_collision_rects
    for obj in self.tmx_data.objects:
      if obj.name == "monster":
        group = obj.properties.get("group", "salle1")
        if group == group_name:
          monster = Monster(obj, collision_list, self.player)
          monster.group = group_name
          monster.map_width = self.tmx_data.width * self.tmx_data.tilewidth
          monster.map_height = self.tmx_data.height * self.tmx_data.tileheight
          self.monsters.add(monster)
          self.group.add(monster)


  def handle_input(self):
    keys = pygame.key.get_pressed()
    dx_keyboard, dy_keyboard = self.calculate_movement(keys)

    # Combine avec joystick (priorité joystick si utilisé)
    jx, jy = self.player.joystick_axis
    if abs(jx) > 0.1 or abs(jy) > 0.1:
        dx, dy = jx * self.player.speed, jy * self.player.speed
        # Choix de direction (pour animation)
        if abs(jx) > abs(jy):
            self.player.direction = "right" if jx > 0 else "left"
        else:
            self.player.direction = "down" if jy > 0 else "up"
    else:
        dx, dy = dx_keyboard, dy_keyboard

    
    self.apply_movement(dx, dy)
    self.update_player_state(dx, dy)

  def calculate_movement(self, keys):
    """Calculate movement based on key presses."""
    dx, dy = 0, 0
    if keys[pygame.K_LEFT]: 
        dx -= 1
        self.player.direction = "left"
    if keys[pygame.K_RIGHT]: 
        dx += 1
        self.player.direction = "right"
    if keys[pygame.K_UP]: 
        dy -= 1
        self.player.direction = "up"
    if keys[pygame.K_DOWN]: 
        dy += 1
        self.player.direction = "down"

    # Normalize diagonal movement
    if dx != 0 and dy != 0:
        dx *= 0.7071
        dy *= 0.7071

    # Apply speed
    dx *= self.player.speed
    dy *= self.player.speed
    return dx, dy

  def apply_movement(self, dx, dy):
    # --- Déplacement horizontal avec logique mur fixe + destructible
    if dx != 0:
        map_w = self.tmx_data.width * self.tmx_data.tilewidth
        old_x = self.player.rect.x
        self.player.rect.x = max(0, min(old_x + dx, map_w - self.player.rect.width))

        # 1) Collision murs fixes ?
        if any(self.player.rect.colliderect(r) for r in self.static_collision_rects):
            self.player.rect.x = old_x
        else:
            # 2) Collision murs destructibles ?
            for wall in list(self.destructible_walls):
                if self.player.rect.colliderect(wall.rect):
                    cost = self.wall_cost + self.destroyed_wall_count * self.destroy_cost_increment
                    # message initial
                    self.collision_message  = f"Coût {cost} pts"
                    self.message_start_time = pygame.time.get_ticks()
                    if self.score >= cost:
                        # détruire + retrait collision
                        #self.score -= cost
                        self.destroyed_wall_count += 1
                        self.collision_message = "Mur détruit !"
                        self.destructible_walls.remove(wall)
                        self.destructible_collision_rects = [
                            r for r in self.destructible_collision_rects
                            if not r.colliderect(wall.rect)
                        ]
                        wall.destroy()
                        self.create_collect_effect(wall.rect.center, is_wall=True)
                    else:
                        # pas assez de score → on bloque le déplacement
                        self.player.rect.x = old_x
                        # bloquer le joueur et message d’échec
                        self.collision_message = f"Score insuffisant ({self.score}/{cost})"
                    break

    # --- Déplacement vertical avec même logique
    if dy != 0:
        map_h = self.tmx_data.height * self.tmx_data.tileheight
        old_y = self.player.rect.y
        self.player.rect.y = max(0, min(old_y + dy, map_h - self.player.rect.height))

        # 1) Collision murs fixes ?
        if any(self.player.rect.colliderect(r) for r in self.static_collision_rects):
            self.player.rect.y = old_y
        else:
            # 2) Collision murs destructibles ?
            for wall in list(self.destructible_walls):
                if self.player.rect.colliderect(wall.rect):
                    cost = self.wall_cost + self.destroyed_wall_count * self.destroy_cost_increment
                    # message initial
                    self.collision_message  = f"Coût {cost} pts"
                    self.message_start_time = pygame.time.get_ticks()
                    if self.score >= cost:
                        #self.score -= cost
                        self.destroyed_wall_count += 1
                        self.collision_message = "Mur détruit !"
                        self.destructible_walls.remove(wall)
                        self.destructible_collision_rects = [
                            r for r in self.destructible_collision_rects
                            if not r.colliderect(wall.rect)
                        ]
                        wall.destroy()
                        self.create_collect_effect(wall.rect.center, is_wall=True)
                    else:
                        self.player.rect.y = old_y
                        self.collision_message = f"Score insuffisant ({self.score}/{cost})"
                    break

  def update_player_state(self, dx, dy):
    """Update the player's movement state and idle image."""
    moving = dx != 0 or dy != 0
    self.player.is_moving = moving
    if not moving:
        self.player.idle_image = self.player.images[self.player.direction][0]

  def show_start_screen(self):
    """Affiche l'écran de démarrage"""
    start_font = pygame.font.Font(None, 65)
    menu_font = pygame.font.Font(None, 50)
    gold = (255, 215, 0)
    white = (255, 255, 255)
    selected_color = (0, 255, 0)
    title_text = start_font.render("Bienvenue dans l'Univers d'Arielle!", True, gold)
    menu_options = self.create_menu_options(menu_font, white)

    blink_timer = pygame.time.get_ticks()
    show_subtitle = True
    selected_index = 0
    running = True

    while running:
      selected_index, running = self.handle_start_screen_events(menu_options, selected_index, running)
      show_subtitle, blink_timer = self.update_blinking_subtitle(blink_timer, show_subtitle)
      self.render_start_screen(title_text, menu_options, selected_index, show_subtitle, selected_color, white)
      pygame.time.Clock().tick(30)

    self.initialize_game_state()
    self.game_loop()

  def create_menu_options(self, menu_font, white):
    """Crée les options du menu avec leur rendu."""
    menu_options = [
        {"text": "Commencer", "action": "start"},
        {"text": "Options", "action": "options"},
        {"text": "Quitter", "action": "quit"}
    ]
    for option in menu_options:
        option["rendered"] = menu_font.render(option["text"], True, white)
    return menu_options

  def handle_start_screen_events(self, menu_options, selected_index, running):
    """Gère les événements de l'écran de démarrage."""
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
          pygame.quit()
          exit()
      if event.type == pygame.KEYDOWN:
          selected_index, running = self.handle_keyboard_events(event, menu_options, selected_index, running)
      if event.type == pygame.MOUSEMOTION:
          selected_index = self.handle_mouse_motion(event, menu_options, selected_index)
      if event.type == pygame.MOUSEBUTTONDOWN:
          running = self.handle_mouse_click(menu_options, selected_index, running)
    return selected_index, running

  def handle_keyboard_events(self, event, menu_options, selected_index, running):
    """Gère les événements clavier."""
    if event.key == pygame.K_UP:
        selected_index = (selected_index - 1) % len(menu_options)
    elif event.key == pygame.K_DOWN:
        selected_index = (selected_index + 1) % len(menu_options)
    elif event.key == pygame.K_RETURN:
        action = menu_options[selected_index]["action"]
        running = self.execute_menu_action(action, running)
    return selected_index, running

  def handle_mouse_motion(self, event, menu_options, selected_index):
    """Gère le survol de la souris."""
    for i, option in enumerate(menu_options):
        text_rect = option["rendered"].get_rect(
            center=(self.screen.get_width() / 2, self.screen.get_height() / 2 + 50 + i * 60)
        )
        if text_rect.collidepoint(event.pos):
            return i
    return selected_index

  def handle_mouse_click(self, menu_options, selected_index, running):
    """Gère les clics de la souris."""
    action = menu_options[selected_index]["action"]
    return self.execute_menu_action(action, running)

  def execute_menu_action(self, action, running):
    """Exécute l'action du menu sélectionné."""
    if action == "start":
        return False
    elif action == "options":
        self.options_menu.run(self)
    elif action == "quit":
        pygame.quit()
        exit()
    return running

  def update_blinking_subtitle(self, blink_timer, show_subtitle):
    """Met à jour l'état du clignotement du sous-titre."""
    current_time = pygame.time.get_ticks()
    if current_time - blink_timer > 500:  # 500 ms entre clignotements
        show_subtitle = not show_subtitle
        blink_timer = current_time
    return show_subtitle, blink_timer

  def render_start_screen(self, title_text, menu_options, selected_index, show_subtitle, selected_color, white):
    """Rend l'écran de démarrage."""
    self.screen.fill((30, 30, 70))  # Fond bleu foncé
    title_rect = title_text.get_rect(center=(self.screen.get_width() / 2, 150))
    self.screen.blit(title_text, title_rect)

    if show_subtitle:
        subtitle_font = pygame.font.Font(None, 36)
        subtitle_text = subtitle_font.render("Utilisez les flèches ou la souris pour naviguer", True, white)
        subtitle_rect = subtitle_text.get_rect(center=(self.screen.get_width() / 2, 220))
        self.screen.blit(subtitle_text, subtitle_rect)

    for i, option in enumerate(menu_options):
        color = selected_color if i == selected_index else white
        text_surface = pygame.font.Font(None, 50).render(option["text"], True, color)
        text_rect = text_surface.get_rect(
            center=(self.screen.get_width() / 2, self.screen.get_height() / 2 + 50 + i * 60)
        )
        self.screen.blit(text_surface, text_rect)

    pygame.display.flip()

  def end_game(self, victory, reason):
    print(f"[INFO] Fin du jeu - {'Victoire' if victory else 'Défaite'} : {reason}")
    if victory:
      return self.win(reason)
    else:
      return self.game_over_screen(reason)

  def navigate_menu(self, direction):
    if self.menu_context == "start_menu":
      if direction == "up":
        self.selected_menu_index = (self.selected_menu_index - 1) % len(self.menu_options)
      elif direction == "down":
        self.selected_menu_index = (self.selected_menu_index + 1) % len(self.menu_options)
    elif self.menu_context == "pause_menu":
      if direction == "up":
        self.pause_selected_index = (self.pause_selected_index - 1) % len(self.pause_menu_options)
      elif direction == "down":
        self.pause_selected_index = (self.pause_selected_index + 1) % len(self.pause_menu_options)

  def validate_menu_selection(self):
    if self.menu_context == "start_menu":
        selected_action = self.menu_options[self.selected_menu_index]["action"]
        self.execute_menu_action(selected_action, True)
    elif self.menu_context == "pause_menu":
        selected_action = self.pause_menu_options[self.pause_selected_index]["action"]
        self.execute_pause_menu_action(selected_action)
    
