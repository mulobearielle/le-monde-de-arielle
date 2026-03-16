import pygame


class DestructibleWall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, requires_monster=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((150, 75, 0))  # Marron pour les murs destructibles
        self.rect = self.image.get_rect(topleft=(x, y))
        self.requires_monster = requires_monster
        self.destroyed = False
    
    def destroy(self):
        if not self.destroyed:
            self.destroyed = True
            self.kill()  # Retire le mur des groupes
            return True
        return False