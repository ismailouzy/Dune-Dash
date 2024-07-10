#usr/bin/env python3
"""enemy class for the game."""

import pygame
import math
from scripts.bullet import Projectile

class Enemy:
    def __init__(self, pos, player, size=32, sound_manager=None):
        self.sound_manager = sound_manager
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.player = player
        self.detect_range = 130
        self.attack_cooldown = 1
        self.time_since_last_attack = 0
        self.projectiles = []
        self.facing_right = True
        self.state = 'idle'
        self.health = 2
        self.is_dead = False
        self.death_animation_complete = False

        self.load_animations()
        self.current_frame = 0
        self.animation_speed = 0.1
        self.animation_time = 0

    def load_animations(self):
        self.animations = {
            'idle': self.load_animation_frames("enemy-idle-", 4),
            'attack': self.load_animation_frames("enemy-attack-", 4),
            'death': self.load_animation_frames("enemy-die-", 4)
        }

    def load_animation_frames(self, prefix, frame_count):
        return [pygame.image.load(f"enemy_sprites/{prefix}{str(i).zfill(2)}.png").convert_alpha() for i in range(frame_count)]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)

    def update(self, dt):
        if self.is_dead:
            self.update_death_animation(dt)
        if self.state == 'dead':
            return
        
        self.time_since_last_attack += dt
        self.update_animation(dt)

        if self.detect_player():
            self.face_player()
            if self.can_shoot():
                self.shoot()
                self.time_since_last_attack = 0
                self.state = 'attack'
            elif self.state == 'attack' and self.current_frame == len(self.animations['attack']) - 1:
                self.state = 'idle'
        else:
            self.state = 'idle'

        self.update_projectiles(dt)

    def detect_player(self):
        distance = math.hypot(self.player.pos[0] - self.pos[0], self.player.pos[1] - self.pos[1])
        return distance <= self.detect_range

    def face_player(self):
        self.facing_right = self.player.pos[0] > self.pos[0]

    def can_shoot(self):
        return (self.time_since_last_attack >= self.attack_cooldown and
                ((self.facing_right and self.player.pos[0] > self.pos[0]) or
                 (not self.facing_right and self.player.pos[0] < self.pos[0])))

    def shoot(self):
        direction = 0 if self.facing_right else math.pi
        speed = 2
        self.projectiles.append(Projectile(self.pos, direction, speed))
        if self.sound_manager:
            self.sound_manager.play_sound('enemy_shot')

    def update_projectiles(self, dt):
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            if projectile.rect().colliderect(self.player.rect()):
                self.projectiles.remove(projectile)
                self.player.take_damage()

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.is_dead = True
            self.current_frame = 0
            self.state = 'death'

    
    def update_death_animation(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            if self.current_frame < len(self.animations['death']) - 1:
                self.current_frame += 1
            else:
                self.death_animation_complete = True

    def update_animation(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.state])

    def get_current_sprite(self):
        frame = self.animations[self.state][self.current_frame]
        return pygame.transform.flip(frame, not self.facing_right, False)

    def render(self, screen, camera):
        if not self.death_animation_complete:
            screen.blit(self.get_current_sprite(), (self.pos[0] - camera.scroll[0], self.pos[1] - camera.scroll[1]))
        for projectile in self.projectiles:
            projectile.render(screen, camera)
