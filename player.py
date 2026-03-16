import pygame
from bullet import Bullet
import os


class Player(pygame.sprite.Sprite):

    def __init__(self, position):
        super().__init__()
        # 1. Charger la sprite sheet
        self.sprite_sheet = pygame.image.load('img/248259.png').convert_alpha()
        sheet_w, sheet_h = self.sprite_sheet.get_size()
        cols, rows = 4, 4  # 4 colonnes × 4 directions
        self.frame_w = sheet_w // cols
        self.frame_h = sheet_h // rows

        # 2. Construire les animations pour chaque direction
        directions = ['down', 'up', 'left', 'right']
        self.images = {}
        for row_idx, dir_name in enumerate(directions):
            frames = []
            for col_idx in range(cols):
                x = col_idx * self.frame_w
                y = row_idx * self.frame_h
                frame = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
                frame.blit(self.sprite_sheet, (0, 0), (x, y, self.frame_w, self.frame_h))
                # Optionnel : redimensionner pour l’écran
                target_w = 25
                scale = target_w / self.frame_w
                frame = pygame.transform.scale(
                    frame,
                    (target_w, int(self.frame_h * scale))
                )
                frames.append(frame)
            self.images[dir_name] = frames

        # 3. Initialisation de l’état du sprite
        self.direction = 'down'
        self.animation_index = 0
        self.animation_speed = 200  # ms entre les frames
        self.last_update = pygame.time.get_ticks()

        # Image et position de départ
        self.idle_image = self.images["down"][0]  # Image au repos
        self.image = self.idle_image  # Attribut requis par pygame.sprite.Sprite
        self.rect = self.image.get_rect(center=(position.x, position.y))

        # Mouvements et tirs
        self.speed = 6
        self.is_moving = False
        self.bullets = pygame.sprite.Group()
        self.last_shot = 0
        self.bullet_power = 50

        self.joystick_axis = [0.0, 0.0]  # [x, y]

    def dash(self):
        print("[MANETTE] dash() appelé — mais non défini")

    def shoot(self):
        now = pygame.time.get_ticks()
        print(f"[SHOOT] Direction actuelle : {self.direction}")
        if now - self.last_shot > 250:
            # Calcul de la position de départ en fonction de la direction
            if self.direction == 'up':
                x = self.rect.centerx
                y = self.rect.top  # Haut du joueur
            elif self.direction == 'down':
                x = self.rect.centerx
                y = self.rect.bottom  # Bas du joueur
            elif self.direction == 'left':
                x = self.rect.left  # Côté gauche du joueur
                y = self.rect.centery
            elif self.direction == 'right':
                x = self.rect.right  # Côté droit du joueur
                y = self.rect.centery
            
            bullet = Bullet(x, y, self.direction, self.bullet_power)
            self.bullets.add(bullet)
            self.last_shot = now

    def update(self):
        now = pygame.time.get_ticks()
        # Si le joueur bouge, on fait tourner l’animation
        if self.is_moving:
            if now - self.last_update > self.animation_speed:
                self.last_update = now
                self.animation_index = (self.animation_index + 1) % len(self.images[self.direction])
                self.image = self.images[self.direction][self.animation_index]
        else:
            # On revient à la frame 0 quand on arrête
            self.animation_index = 0
            self.image = self.images[self.direction][0]

        # Mettre à jour les balles
        self.bullets.update()

    