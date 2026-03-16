import pygame
import math
import random
from player import Bullet

import os

class Monster(pygame.sprite.Sprite):
    def __init__(self, tmx_object, collision_rects, player, zone_rect=None):
        super().__init__()
        # 1. Charger la sprite sheet
        self.sprite_sheet = pygame.image.load('img/monster.png').convert_alpha()
        sheet_w, sheet_h = self.sprite_sheet.get_size()
        cols, rows = 2, 4  # 2 colonnes × 4 directions
        self.frame_w = sheet_w // cols
        self.frame_h = sheet_h // rows
        self.frame_size = (self.frame_w, self.frame_h)
        self.zone_rect = zone_rect

        # 2. Construire les animations
        directions = ['down', 'up', 'left', 'right']
        self.images = {}
        for row_idx, dir_name in enumerate(directions):
            frames = []
            for col_idx in range(cols):
                x = col_idx * self.frame_w
                y = row_idx * self.frame_h
                frame = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
                frame.blit(self.sprite_sheet, (0, 0), (x, y, self.frame_w, self.frame_h))
                # Optionnel : redimensionner si nécessaire
                target_w = 35
                scale = target_w / self.frame_w
                frame = pygame.transform.scale(
                    frame,
                    (target_w, int(self.frame_h * scale))
                )
                frames.append(frame)
            self.images[dir_name] = frames

        # 3. État initial
        self.player = player
        self.rect = self.images['down'][0].get_rect(center=(tmx_object.x, tmx_object.y))
        self.direction = 'down'
        self.animation_index = 0
        self.animation_speed = 200
        self.last_update = pygame.time.get_ticks()
        self.speed = 3
        self.collision_rects = collision_rects

        self.is_boss = getattr(tmx_object, "name", "") == "final_boss"
        # initialisation de la santé
        self.max_health = 100          # ajustez selon la difficulté
        self.health     = self.max_health


        # Compteur de collisions et portée de détection initiale
        self.collision_count = 0
        # Portée de détection initiale
        self.base_detection_range = 900
        self.detection_range = self.base_detection_range
        # Image courante et position
        self.image = self.images[self.direction][0]
        self.rect = self.image.get_rect(center=(tmx_object.x, tmx_object.y))
        # Propriétés de l'aura (effets visuels lors de la détection)
        self.show_aura = False
        self.aura_alpha = 0
        self.aura_duration = 1000          # Durée de l'effet en ms
        self.aura_start_time = 0
        # Texte temporaire (+Portée!)  
        self.text_timer = 0
        self.text_pos = (0, 0)
        self.effect_font = pygame.font.Font(None, 24)


    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > 500:
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, self.bullet_power)
            self.bullets.add(bullet)
            self.last_shot = now

    def draw_health_bar(self, surface):
        """Dessine une jauge de vie au-dessus du sprite."""
        bar_width  = self.rect.width
        bar_height = 5
        # bordure noire
        outline = pygame.Rect(
            self.rect.x - 2,
            self.rect.y - bar_height - 2,
            bar_width + 4,
            bar_height + 4
        )
        pygame.draw.rect(surface, (0, 0, 0), outline)
        # fond rouge
        bg_rect = pygame.Rect(
            self.rect.x,
            self.rect.y - bar_height - 1,
            bar_width,
            bar_height
        )
        pygame.draw.rect(surface, (255, 0, 0), bg_rect)
        # santé restante en vert
        fg_width = int(bar_width * (self.health / self.max_health))
        fg_rect  = pygame.Rect(
            self.rect.x,
            self.rect.y - bar_height - 1,
            fg_width,
            bar_height
        )
        pygame.draw.rect(surface, (0, 255, 0), fg_rect)
        
    def take_damage(self, amount):
        """Réduit la vie et tue le monstre si elle tombe à zéro."""
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def update(self):
        # Calcul du vecteur vers le joueur
        dx = self.player.rect.x - self.rect.x
        dy = self.player.rect.y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist > 0 and dist < getattr(self, 'detection_range', math.inf):
            # Choix de la direction
            if abs(dy) > abs(dx):
                self.direction = 'up' if dy < 0 else 'down'
            else:
                self.direction = 'left' if dx < 0 else 'right'
            # Déplacement
            dxn, dyn = dx / dist * self.speed, dy / dist * self.speed
            self.rect.x += dxn
            if any(self.rect.colliderect(r) for r in self.collision_rects):
                self.rect.x -= dxn
            self.rect.y += dyn
            if any(self.rect.colliderect(r) for r in self.collision_rects):
                self.rect.y -= dyn
            # Animation
            now = pygame.time.get_ticks()
            if now - self.last_update > self.animation_speed:
                self.last_update = now
                self.animation_index = (self.animation_index + 1) % len(self.images[self.direction])
                self.image = self.images[self.direction][self.animation_index]
        else:
            # Idle
            self.animation_index = 0
            self.image = self.images['down'][0]

    def reset_position(self):
        """Position aléatoire dans la zone définie, sans chevauchement"""
        max_attempts = 100
        safe_margin = 50

        for _ in range(max_attempts):
            # Générer une position aléatoire dans la zone définie
            if self.zone_rect:
                new_x = random.randint(
                    int(self.zone_rect.left), 
                    int(self.zone_rect.right - self.rect.width)
                )
                new_y = random.randint(
                    int(self.zone_rect.top), 
                    int(self.zone_rect.bottom - self.rect.height)
                )
            else:
                new_x = random.randint(
                    safe_margin, 
                    self.map_width - self.rect.width - safe_margin
                )
                new_y = random.randint(
                    safe_margin, 
                    self.map_height - self.rect.height - safe_margin
                )

            self.rect.topleft = (new_x, new_y)

            # Vérifie les collisions
            if not self.check_collision():
                return

        # Si tous les essais échouent, placer au centre de la map
        self.rect.center = (self.map_width // 2, self.map_height // 2)

    def increase_detection(self, sound_effect):
        """Augmente la portée de détection de 20% par collision (max 600)"""
        self.collision_count += 1
        self.detection_range = min(
            self.base_detection_range * (1 + 0.2 * self.collision_count),
            800  # Maximum 200% de la portée initiale
        )
        print(f"Nouvelle portée: {self.detection_range}px")  # Debug

        # Active les effets
        self.show_aura = True
        self.aura_alpha = 150  # Opacité initiale
        self.aura_start_time = pygame.time.get_ticks()
        self.text_timer = pygame.time.get_ticks()
        self.text_pos = (self.rect.centerx, self.rect.top - 20)
        
        # Joue le son
        sound_effect.play()
    
    

    

    def move(self, dx, dy):
        # Déplacement X
        self.rect.x += dx
        if self.check_collision():
            self.rect.x -= dx
            
        # Déplacement Y
        self.rect.y += dy
        if self.check_collision():
            self.rect.y -= dy

    def check_collision(self):
        return any(self.rect.colliderect(rect) for rect in self.collision_rects)

    def animate(self, dx, dy):
        now = pygame.time.get_ticks()
        
        # Détermination de la direction avec priorité verticale
        if abs(dy) > abs(dx):
            direction = "up" if dy < 0 else "down"
        else:
            direction = "right" if dx > 0 else "left"

        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.animation_index = (self.animation_index + 1) % 2
            self.image = self.images[direction][self.animation_index]


    def draw_effects(self, screen):
        now = pygame.time.get_ticks()
        
        # Aura rouge
        if self.show_aura:
            aura_radius = int(self.detection_range * 0.8)
            aura_surface = pygame.Surface((aura_radius*2, aura_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, (255, 0, 0, self.aura_alpha), 
                            (aura_radius, aura_radius), aura_radius)
            screen.blit(aura_surface, (self.rect.centerx - aura_radius, 
                                    self.rect.centery - aura_radius))
            
            # Fade out progressif
            if now - self.aura_start_time > self.aura_duration:
                self.show_aura = False
            else:
                self.aura_alpha = int(150 * (1 - (now - self.aura_start_time)/self.aura_duration))

        # Texte temporaire
        if now - self.text_timer < 1500:  # 1.5 secondes
            text = self.effect_font.render("+ Portée!", True, (255, 215, 0))  # Or
            text_rect = text.get_rect(center=self.text_pos)
            screen.blit(text, text_rect)

