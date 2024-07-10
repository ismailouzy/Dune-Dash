import pygame
import csv
from scripts.sound import SoundManager
from scripts.player import Player
from scripts.bullet import Projectile
from scripts.coins import Coin
from scripts.Camera import Camera
from scripts.enemy import Enemy



class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font('nasalization-rg.otf', 36)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Game:
    def __init__(self, width=800, height=600, start_x=None, end_x=None):
        pygame.init()
        self.width = width
        self.height = height
        pygame.display.set_caption('Dunes Dash')
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.in_menu = True
        self.sound_manager = SoundManager()
        self.sound_manager.play_music('menu')

        self.tile_size = 40
        self.load_map("map.csv")
        # Set default start_x if not provided
        self.start_x = start_x if start_x is not None else self.tile_size
        
        # Set default end_x if not provided (rightmost edge of the map)
        self.end_x = end_x if end_x is not None else len(self.map[0]) * self.tile_size

        self.player = Player((self.start_x, 300), 36, self.sound_manager)
        self.set_map_boundaries()
        self.camera = Camera(self.width, self.height, len(self.map))
        self.movement = [False, False]

        self.load_tiles()
        self.bg = pygame.image.load("bg.png").convert()
        self.bg = pygame.transform.scale(self.bg, (width, height))
        
        self.bgmenu = pygame.image.load("menu.png").convert()
        self.bgmenu = pygame.transform.scale(self.bgmenu, (width, height))

        self.coins = []
        self.load_coins()

        self.enemies = []
        self.load_enemies()

        self.font = pygame.font.Font('sofachrome-rg.otf', 21)
        
        self.play_button = Button(300, 250, 200, 50, "Play", (0, 255, 0), (0, 0, 0))
        self.exit_button = Button(300, 350, 200, 50, "Exit", (255, 0, 0), (0, 0, 0))
        
    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button.is_clicked(event.pos):
                    self.in_menu = False
                    self.sound_manager.stop_music()
                    self.sound_manager.play_music('game')
                elif self.exit_button.is_clicked(event.pos):
                    self.running = False

    def render_menu(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bgmenu, (0, 0))
        self.play_button.draw(self.screen)
        self.exit_button.draw(self.screen)
        pygame.display.flip()
    
    def load_coins(self):
        self.coins = [
            Coin((300, 444), sound_manager=self.sound_manager),
            Coin((600, 484), sound_manager=self.sound_manager),
            Coin((682, 324), sound_manager=self.sound_manager),
            Coin((214, 324), sound_manager=self.sound_manager),
            Coin((1070, 284), sound_manager=self.sound_manager)
        ]

    def load_enemies(self):
        self.enemies = [
            Enemy((400, 444), self.player, sound_manager=self.sound_manager),
            Enemy((700, 484), self.player, sound_manager=self.sound_manager),
            Enemy((426, 284), self.player, sound_manager=self.sound_manager),
            Enemy((1220, 364), self.player, sound_manager=self.sound_manager)
            
        ]

    def get_coins(self):
        coins_to_remove = []
        for coin in self.coins:
            if coin.collect(self.player):
                coins_to_remove.append(coin)
                self.player.coins += 1
        for coin in coins_to_remove:
            self.coins.remove(coin)

    def load_tiles(self):
        self.tiles = {}
        self.nottiles = {}
        for i in range(1, 17):
            try:
                tile_image = pygame.image.load(f"Tile/{i}.png").convert_alpha()
                tile_image = pygame.transform.scale(tile_image, (self.tile_size, self.tile_size))
                self.tiles[str(i)] = tile_image
            except pygame.error:
                print(f"Warning: Could not load tile image {i}.png")
        
        for i in range(17, 68):
            try:
                tile_image = pygame.image.load(f"Tile/{i}.png").convert_alpha()
                tile_image = pygame.transform.scale(tile_image, (self.tile_size, self.tile_size))
                self.nottiles[str(i)] = tile_image
            except pygame.error:
                print(f"Warning: Could not load tile image {i}.png")

    def load_map(self, filename):
        self.map = []
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                self.map.append(row)
    
    def set_map_boundaries(self):
        self.player.min_x = self.start_x
        self.player.max_x = self.end_x

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = True
                if event.key == pygame.K_RIGHT:
                    self.movement[1] = True
                if event.key == pygame.K_DOWN:
                    self.player.duck(True)
                if event.key == pygame.K_UP:
                    self.player.jump()
                if event.key == pygame.K_SPACE:
                    self.player.attack(self.enemies)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.movement[0] = False
                if event.key == pygame.K_RIGHT:
                    self.movement[1] = False
                if event.key == pygame.K_DOWN:
                    self.player.duck(False)

    def update(self, dt):
        self.player.update(dt)
        print(self.player.pos)
        self.player.player_mov(
            (self.movement[1] - self.movement[0], 0), 
            self.get_platforms(), 
            dt
        )
        # Update camera only if player is within the scrollable range
        if self.player.pos[0] > self.width // 2 and self.player.pos[0] < self.end_x - self.width // 2:
            self.camera.update(self.player)
        self.get_coins()

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt)
            for projectile in enemy.projectiles[:]:
                if projectile.rect().colliderect(self.player.rect()):
                    enemy.projectiles.remove(projectile)
                    self.player.take_damage()
            if enemy.death_animation_complete:
                self.enemies.remove(enemy)

        # Check for game over
        if self.player.health <= 0:
            self.game_over()

    def render(self):
        self.screen.fill((0, 0, 0))

        # Draw background
        bg_scroll = [x % self.bg.get_width() for x in self.camera.scroll]
        self.screen.blit(self.bg, (-bg_scroll[0], 0))
        self.screen.blit(self.bg, (-bg_scroll[0] + self.bg.get_width(), 0))

        # Draw tiles
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                if tile != '0' and tile in self.tiles:
                    tile_x = x * self.tile_size - self.camera.scroll[0]
                    tile_y = y * self.tile_size - self.camera.scroll[1]
                    if -self.tile_size <= tile_x < self.width and -self.tile_size <= tile_y < self.height:
                        self.screen.blit(self.tiles[tile], (tile_x, tile_y))
        
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                if tile != '0' and tile in self.nottiles:
                    tile_x = x * self.tile_size - self.camera.scroll[0]
                    tile_y = y * self.tile_size - self.camera.scroll[1]
                    if -self.tile_size <= tile_x < self.width and -self.tile_size <= tile_y < self.height:
                        self.screen.blit(self.nottiles[tile], (tile_x, tile_y))
        
        # Draw coins
        for coin in self.coins:
            coin.render(self.screen, self.camera)

        # Draw enemies
        for enemy in self.enemies:
            
            enemy.render(self.screen, self.camera)

        # Draw player
        player_pos = self.camera.apply(self.player)
        self.screen.blit(self.player.get_current_sprite(), player_pos)

        # Render UI
        coin_text = self.font.render(f"Coins: {self.player.coins}", True, (255, 255, 0))
        health_text = self.font.render(f"Health: {self.player.health}", True, (255, 0, 0))
        self.screen.blit(coin_text, (10, 10))
        self.screen.blit(health_text, (10, 50))

        pygame.display.flip()

    def get_platforms(self):
        platforms = []
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                if tile != '0' and tile in self.tiles:
                    platforms.append(pygame.Rect(
                        x * self.tile_size,
                        y * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    ))
        return platforms

    def game_over(self):
        self.sound_manager.stop_music()
        self.sound_manager.play_sound('game_over')
        game_over_text = self.font.render("GAME OVER!", True, (255, 0, 0))
        self.screen.blit(game_over_text, (self.width // 2 - 100, self.height // 2))
        pygame.display.flip()
        pygame.time.wait(2000)  # Wait for 2 seconds
        self.running = False

    def run(self):
        while self.running:
            if self.in_menu:
                self.handle_menu_events()
                self.render_menu()
            else:
                dt = self.clock.tick(60) / 1000.0
                self.handle_events()
                self.update(dt)
                self.render()

if __name__ == "__main__":
    game = Game(start_x=0, end_x=1500)
    game.run()