# game.py

import pygame
import sys
import time
import random
import math
import logging

from config import Config
from state import GameState
from utils import is_night
from map_gen import generate_island_map
from entities import Player
from hud import HUD
from screens import TitleScreen, IntroScreen, HelpScreen, PauseScreen, LoseScreen, WinScreen
from sound_manager import sound_manager

# Newly imported modules
import spawn_manager
import collision_manager
import boat_manager
import input_manager

logger = logging.getLogger(__name__)

joystick_handler = None
if Config.ENABLE_JOYSTICK:
    try:
        from joystick_handler import JoystickHandler
        joystick_handler = JoystickHandler()
    except Exception as e:
        logger.warning(f"Failed to initialize joystick handler: {e}")
        joystick_handler = None

class Game:
    """
    The main game class, now primarily an orchestrator that delegates tasks.
    """
    def __init__(self) -> None:
        pygame.init()
        self.window = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption("Flucht von der Dinosaurier Insel")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)

        self.state = GameState.MAIN_MENU
        self.running = True

        # Screens
        self.title_screen = TitleScreen(self.window)
        self.intro_screen = IntroScreen(self.window)
        self.help_screen = HelpScreen(self.window)
        self.pause_screen = PauseScreen(self.window)
        self.lose_screen = LoseScreen(self.window)
        self.win_screen = WinScreen(self.window)

        self.hud = None
        self.reset_game()
        sound_manager.play("actions", "game_start")

    def reset_game(self) -> None:
        """
        Reset game state: generate map, create Player, spawn items/dinosaurs,
        and set up boat frames, etc.
        """
        logger.info("Resetting game state...")
        self.game_map = generate_island_map()
        cx = Config.MAP_WIDTH // 2
        cy = Config.MAP_HEIGHT // 2

        self.player = Player(cx, cy)
        self.hud = HUD(self.player, self)
        self.items = []
        self.dinosaurs = []

        # Spawn items, dinosaurs
        spawn_manager.spawn_items(self, count=6)
        spawn_manager.spawn_dinosaurs(
            self,
            n_normal=Config.DINOSAUR_COUNT_NORMAL,
            n_aggressive=Config.DINOSAUR_COUNT_AGGRESSIVE
        )

        # Boat
        self.boat_active = False
        self.boat_x = None
        self.boat_y = None
        self.boat_frames = boat_manager.create_boat_frames()
        self.boat_current_frame = 0
        self.boat_animation_timer = 0.0
        self.boat_animation_interval = 0.3

        # Lava
        self.lava_fields = []
        self.last_lava_time = time.time()
        self.start_time = time.time()

        # Camera
        self.camx = self.player.x
        self.camy = self.player.y
        self.old_night_state = None

        # Start background music
        sound_manager.play_music()

    def run(self) -> None:
        """
        Main game loop: handle events, update, draw.
        """
        try:
            while self.running:
                dt = self.clock.tick(Config.FPS) / 1000.0
                events = pygame.event.get()

                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                    # Delegate event logic to input_manager
                    input_manager.handle_state_event(self, event)

                # Joystick
                if Config.ENABLE_JOYSTICK and joystick_handler:
                    joystick_actions = joystick_handler.process_events(events)
                    for action in joystick_actions:
                        if action == 'activate_repellent':
                            if self.player.inventory.get("repellent", 0) > 0:
                                self.player.trigger_repellent()
                                self.hud.trigger_flash((0, 0, 255), 100, 0.2)

                if self.state == GameState.PLAYING:
                    self.update_playing(dt)

                self.draw()
                pygame.display.flip()

        except Exception as e:
            logger.error(f"Caught exception in main loop: {e}")
        finally:
            if joystick_handler:
                joystick_handler.quit()
            pygame.quit()
            sys.exit()

    def update_playing(self, dt: float) -> None:
        """
        Update logic for the PLAYING state.
        """
        # Movement
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])

        if Config.ENABLE_JOYSTICK and joystick_handler:
            jdx, jdy = joystick_handler.get_movement()
            dx += jdx
            dy += jdy

        dx *= Config.PLAYER_SPEED
        dy *= Config.PLAYER_SPEED
        self.player.move(dx, dy, self.game_map)
        self.player.update(dt)
        self.hud.update(dt)

        # Day/Night
        now = time.time()
        current_time = now - self.start_time
        night = is_night(current_time)
        if self.old_night_state is None:
            self.old_night_state = night
        else:
            if night != self.old_night_state:
                self.old_night_state = night

        # Lava check
        if now - self.last_lava_time > Config.LAVA_INTERVAL:
            self.lava_fields = spawn_manager.spawn_lava(self)
            self.last_lava_time = now

        # Update dinos
        for dino in self.dinosaurs:
            dino.update(self.player, self.game_map, night)

        # Collision checks
        collision_manager.check_collisions(self)

        # Camera
        self.camx = self.player.x
        self.camy = self.player.y

        # Boat arrival
        cycles_passed = int(current_time // Config.CYCLE_LENGTH)
        if (cycles_passed >= Config.BOAT_ARRIVAL_CYCLES) and not self.boat_active:
            self.boat_active = True
            boat_manager.place_boat(self)

        # Win/Lose conditions
        if self.boat_active and self.boat_x is not None:
            if int(self.player.x) == self.boat_x and int(self.player.y) == self.boat_y:
                sound_manager.play("actions", "win_game")
                self.state = GameState.WON

        if self.player.hp <= 0:
            sound_manager.play("actions", "game_over")
            self.state = GameState.GAME_OVER

        # Boat animation
        if self.boat_active:
            self.boat_animation_timer += dt
            if self.boat_animation_timer >= self.boat_animation_interval:
                self.boat_animation_timer = 0.0
                self.boat_current_frame = (self.boat_current_frame + 1) % len(self.boat_frames)

    def draw(self) -> None:
        """
        Main draw method, calls draw_{map,entities,etc.}
        """
        self.window.fill((30, 30, 30))
        if self.state == GameState.MAIN_MENU:
            self.title_screen.draw()
        elif self.state == GameState.INTRO:
            self.intro_screen.draw()
        elif self.state == GameState.HELP:
            self.help_screen.draw()
        elif self.state == GameState.PAUSE:
            self.pause_screen.draw()
        elif self.state == GameState.GAME_OVER:
            self.lose_screen.draw()
        elif self.state == GameState.WON:
            self.win_screen.draw()
        elif self.state == GameState.PLAYING:
            self.draw_playing()

    def draw_playing(self) -> None:
        self.draw_map()
        self.draw_entities()
        self.hud.draw(self.window)

        # Night overlay
        now = time.time()
        if is_night(now - self.start_time):
            overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill(Config.NIGHT_OVERLAY)
            self.window.blit(overlay, (0, 0))

    def draw_map(self) -> None:
        tile_cols = Config.WINDOW_WIDTH // Config.TILE_SIZE
        tile_rows = Config.WINDOW_HEIGHT // Config.TILE_SIZE

        start_x = max(0, int(self.camx) - tile_cols // 2 - 1)
        end_x = min(Config.MAP_WIDTH, int(self.camx) + tile_cols // 2 + 2)
        start_y = max(0, int(self.camy) - tile_rows // 2 - 1)
        end_y = min(Config.MAP_HEIGHT, int(self.camy) + tile_rows // 2 + 2)

        for ty in range(start_y, end_y):
            for tx in range(start_x, end_x):
                tile_id = self.game_map[ty][tx]
                c = Config.BIOMES[tile_id]["color"]
                if (tx, ty) in self.lava_fields:
                    c = (255, 0, 0)  # Lava
                sx, sy = self.world_to_screen(tx, ty)
                pygame.draw.rect(self.window, c, (sx, sy, Config.TILE_SIZE, Config.TILE_SIZE))

        # Boat
        if self.boat_active and self.boat_x is not None:
            bx, by = self.boat_x, self.boat_y
            if start_x <= bx < end_x and start_y <= by < end_y:
                sx, sy = self.world_to_screen(bx, by)
                self.window.blit(self.boat_frames[self.boat_current_frame], (sx, sy))

    def draw_entities(self) -> None:
        # Player
        sx, sy = self.world_to_screen(self.player.x, self.player.y)
        self.window.blit(self.player.get_current_frame(), (sx, sy))

        # Dinosaurs
        for dino in self.dinosaurs:
            dsx, dsy = self.world_to_screen(dino.x, dino.y)
            self.window.blit(dino.get_current_frame(), (dsx, dsy))

        # Items
        for it in self.items:
            isx, isy = self.world_to_screen(it.x, it.y)
            self.window.blit(it.get_current_frame(), (isx, isy))

    def world_to_screen(self, wx: float, wy: float) -> tuple[int, int]:
        """
        Convert world coords to screen coords based on the camera.
        """
        sx = (wx - self.camx) * Config.TILE_SIZE + Config.WINDOW_WIDTH // 2
        sy = (wy - self.camy) * Config.TILE_SIZE + Config.WINDOW_HEIGHT // 2
        return int(sx), int(sy)
