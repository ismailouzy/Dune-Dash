#usr/bin/env python3
"""player class for the game."""

import pygame
from scripts.sound import SoundManager

class Player:
    def __init__(self, pos, size=32, sound_manager=None):
        self.sound_manager = sound_manager
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.on_ground = False
        self.facing_right = True
        self.is_walking = False
        self.started_moving = False
        self.is_ducking = False
        self.is_attacking = False
        self.is_jumping = False
        self.jump_buffer = 0
        self.coyote_time = 0
        self.ground_buffer = 0 
        self.coins = 0
        self.health = 4
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.min_x = 0  # Minimum x-coordinate (left boundary)
        self.max_x = 0  # Maximum x-coordinate (right boundary)
        
        self.load_animations()
        self.current_frame = 0
        self.animation_speed = 0.08
        self.animation_time = 0

    def load_animations(self):
        self.animations = {
            'idle': self.load_animation_frames("adventurer-idle-", 2),
            'walk': self.load_animation_frames("adventurer-run-", 6),
            'attack': self.load_animation_frames("adventurer-attack1-", 5),
            'duck': self.load_animation_frames("adventurer-crouch-", 4),
            'jump': self.load_animation_frames("adventurer-jump-", 4),
            'fall': self.load_animation_frames("adventurer-fall-", 2)
        }

    def load_animation_frames(self, prefix, frame_count):
        return [pygame.image.load(f"sprite/{prefix}{str(i).zfill(2)}.png").convert_alpha() for i in range(frame_count)]

    def determine_animation_state(self):
        if self.is_attacking:
            return 'attack'
        if self.is_ducking:
            return 'duck'
        if self.is_jumping:
            return 'jump'
        if not self.on_ground and self.ground_buffer <= 0:
            return 'fall'
        if self.is_walking:
            return 'walk'
        return 'idle'

    def update_animation(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.determine_animation_state()])
            
            if self.is_attacking and self.current_frame == 0:
                self.is_attacking = False

    def get_current_frame_set(self):
        return self.animations[self.determine_animation_state()]

    def get_current_sprite(self):
        frame_set = self.get_current_frame_set()
        self.current_frame = self.current_frame % len(frame_set)
        frame = frame_set[self.current_frame]
        return pygame.transform.flip(frame, not self.facing_right, False)

    def rect(self,n=1):
        return pygame.Rect(self.pos[0], self.pos[1], self.size, self.size*n)

    def player_mov(self, movement=(0, 0), platforms=[], dt=1/60):
        if not self.is_attacking:
            self.is_walking = movement[0] != 0
            if movement[0] > 0:
                self.facing_right = True
                self.started_moving = True
            elif movement[0] < 0:
                self.facing_right = False
                self.started_moving = True

            if self.is_ducking:
                self.velocity[0] = 0
            else:
                self.velocity[0] = movement[0] * 2
                # Check if the player would move past the min_x or max_x
                new_x = self.pos[0] + self.velocity[0]
                if new_x < self.min_x:
                    self.pos[0] = self.min_x
                    self.velocity[0] = 0
                elif new_x > self.max_x - self.size:
                    self.pos[0] = self.max_x - self.size
                    self.velocity[0] = 0
                else:
                    self.pos[0] = new_x
                self.check_horizontal_collisions(platforms)

            self.velocity[1] = min(5, self.velocity[1] + 0.5)
            self.pos[1] += self.velocity[1]
            self.check_vertical_collisions(platforms)

            if self.jump_buffer > 0:
                self.jump_buffer -= dt

            if self.jump_buffer > 0 and (self.on_ground or self.coyote_time > 0):
                self.velocity[1] = -10
                self.on_ground = False
                self.is_jumping = True
                self.jump_buffer = 0
                self.coyote_time = 0
                self.ground_buffer = 0
                
        if self.on_ground:
            self.ground_buffer = 0.1
        elif self.ground_buffer > 0:
            self.ground_buffer -= dt

        if not self.on_ground and self.velocity[1] > 0:
            self.is_jumping = False

    def check_horizontal_collisions(self, platforms):
        player_rect = self.rect()
        for platform in platforms:
            if player_rect.colliderect(platform):
                if self.velocity[0] > 0:
                    self.pos[0] = platform.left - self.size
                elif self.velocity[0] < 0:
                    self.pos[0] = platform.right
                self.velocity[0] = 0

    def check_vertical_collisions(self, platforms):
        was_on_ground = self.on_ground
        self.on_ground = False
        player_rect = self.rect()
        for platform in platforms:
            if player_rect.colliderect(platform):
                if self.velocity[1] > 0:
                    self.pos[1] = platform.top - self.size
                    self.on_ground = True
                    self.velocity[1] = 0
                elif self.velocity[1] < 0:
                    self.pos[1] = platform.bottom
                self.velocity[1] = 0

        if was_on_ground and not self.on_ground:
            self.coyote_time = 0.1

    def jump(self):
        self.jump_buffer = 0.1
        if self.sound_manager:
            self.sound_manager.play_sound('jump')

    def duck(self, is_ducking):
        self.is_ducking = is_ducking
        if is_ducking and self.sound_manager:
            self.sound_manager.play_sound('crouch')

    def attack(self, enemies):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_frame = 0
            attack_rect = self.rect().inflate(20, 0)
            for enemy in enemies:
                if attack_rect.colliderect(enemy.rect()):
                    enemy.take_damage()
            if self.sound_manager:
                self.sound_manager.play_sound('player_shot')

    def take_damage(self):
        if not self.invulnerable:
            self.health -= 1
            self.invulnerable = True
            self.invulnerable_timer = 1
            if self.sound_manager:
                self.sound_manager.play_sound('player_hit')

    def update(self, dt):
        self.update_animation(dt)
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False