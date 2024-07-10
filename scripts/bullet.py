#usr/bin/env python3
"""projectile class for the game."""
import pygame
import math



class Projectile:
    def __init__(self, pos, direction, speed):
        self.pos = list(pos)
        self.direction = direction
        self.speed = speed
        self.size = 9
        self.image = pygame.image.load("projectile.png")
        self.image.set_colorkey((255,255,255))
        self.image.convert()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

    def update(self, dt):
        self.pos[0] += math.cos(self.direction) * self.speed
        

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)

    def render(self, screen, camera):
        screen.blit(self.image, (self.pos[0] - camera.scroll[0], self.pos[1] - camera.scroll[1]))
