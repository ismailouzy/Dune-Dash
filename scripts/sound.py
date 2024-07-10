#usr/bin/env python3
"""Sound manager for the game."""

import pygame

pygame.mixer.init()

class SoundManager:
    def __init__(self):
        self.sounds = {
            'jump': pygame.mixer.Sound('sounds/jump.wav'),
            'crouch': pygame.mixer.Sound('sounds/crouch.wav'),
            'enemy_shot': pygame.mixer.Sound('sounds/enemy_shot.wav'),
            'player_shot': pygame.mixer.Sound('sounds/player_shot.wav'),
            'player_hit': pygame.mixer.Sound('sounds/player_hit.mp3'),
            'coin_collect': pygame.mixer.Sound('sounds/coin_collect.wav'),
            'game_over': pygame.mixer.Sound('sounds/game_over.wav')
        }
        self.music = {
            'menu': 'sounds/menu_music.mp3',
            'game': 'sounds/game_music.mp3'
        }

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def play_music(self, music_name):
        if music_name in self.music:
            pygame.mixer.music.load(self.music[music_name])
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely

    def stop_music(self):
        pygame.mixer.music.stop()