import pygame
import random

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, color):
        super().__init__()
        self.image = pygame.Surface((8,8), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.velocity = [random.uniform(-2, 2), random.uniform(-2, 2)]
        self.lifetime = 30

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.lifetime -= 1
        # Add fade effect
        if self.lifetime < 10:
            alpha = int(255 * (self.lifetime / 10))
            self.image.set_alpha(alpha)
        if self.lifetime <= 0:
            self.kill()