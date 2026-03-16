import pygame
import os



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, power):
        super().__init__()
        self.image = pygame.image.load("img/bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))

        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 10
        self.power = power

    def update(self):
        if self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed
        elif self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed

        
