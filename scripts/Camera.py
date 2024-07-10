#usr/bin/env python3
"""Camera class for the game."""

import pygame



class Camera:
    def __init__(self, width, height, map_height, map_width=0):
        self.width = width
        self.height = height
        self.scroll = [0, 0]
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = 32
        self.max_scroll_y = self.map_height * self.tile_size - height
        self.min_scroll_x = 100
        self.max_scroll_x = self.map_width * self.tile_size - width - 100

    def apply(self, entity):
        return [entity.pos[0] - self.scroll[0], entity.pos[1] - self.scroll[1]]

    def update(self, target):
        self.scroll[0] += (target.pos[0] - self.scroll[0] - self.width // 2) // 20
        
        if target.pos[1] < self.max_scroll_y + self.height:
            target_scroll_y = max(0, min(target.pos[1] - self.height // 2, self.max_scroll_y))
            self.scroll[1] += (target_scroll_y - self.scroll[1]) // 20
        
        self.scroll[1] = max(0, self.scroll[1])
