#usr/bin/env python3
"""coin class for the game."""

import pygame


class Coin:
    def __init__(self, pos, size=25, sound_manager=None):
        self.sound_manager = sound_manager
        self.pos = pos
        self.size = size
        self.image = pygame.image.load("coin.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.image.set_colorkey((255, 255, 255))
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)

    def render(self, screen, camera):
        screen.blit(self.image, (self.pos[0] - camera.scroll[0], self.pos[1] - camera.scroll[1]))

    def collect(self, player):
        if self.rect.colliderect(player.rect()):
            if self.sound_manager:
                self.sound_manager.play_sound('coin_collect')
            return True
        return False