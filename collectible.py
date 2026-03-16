import pygame
import os

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.value = 10  # Valeur par défaut

        # Vérification du chemin de l'image
        if not os.path.exists(image_path):
            print(f"Erreur : Fichier image introuvable - {image_path}")
            image_path = None

        try:
            if image_path:
                self.image = pygame.image.load(image_path).convert_alpha()
            else:
                raise FileNotFoundError
        except (pygame.error, FileNotFoundError):
            # Création d'une surface par défaut si l'image ne peut être chargée
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            self.image.fill((255, 255, 0))  # Jaune par défaut
        
        self.rect = self.image.get_rect(topleft=(x, y))

class SpecialCollectible(Collectible):
    def __init__(self, x, y, image_path, effect_type, effect_value):
        super().__init__(x, y, image_path)
        self.effect_type = effect_type  # 'speed', 'jump', 'time', 'score', 'bullet'
        self.effect_value = effect_value
        self.value = 0 if effect_type != 'score' else effect_value
        