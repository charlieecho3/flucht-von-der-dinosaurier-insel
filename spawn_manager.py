# spawn_manager.py

from __future__ import annotations
import random
import logging
from typing import TYPE_CHECKING

from config import Config
from entities import Dinosaur, Item
from utils import is_passable, get_random_passable_tile

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # Only imported at type-check time, avoids runtime circular import
    from game import Game

def spawn_items(game: Game, count: int = 6) -> None:
    """
    Spawn a given number of items (potions/repellent) near the map center.
    """
    center_x = Config.MAP_WIDTH // 2
    center_y = Config.MAP_HEIGHT // 2
    for _ in range(count):
        t = random.choice(["potion", "repellent"])
        rx = center_x + random.randint(-15, 15)
        ry = center_y + random.randint(-15, 15)
        if 0 <= rx < Config.MAP_WIDTH and 0 <= ry < Config.MAP_HEIGHT:
            if is_passable(rx, ry, game.game_map):
                game.items.append(Item(rx, ry, t))
    logger.info(f"Spawned {len(game.items)} items. (requested {count})")

def spawn_dinosaurs(game: Game, n_normal: int, n_aggressive: int) -> None:
    """
    Spawn normal and aggressive dinosaurs.
    """
    for _ in range(n_normal):
        x, y = get_random_passable_tile(game.game_map, for_dino=True)
        game.dinosaurs.append(Dinosaur(x, y, aggressive=False))

    for _ in range(n_aggressive):
        x, y = get_random_passable_tile(game.game_map, for_dino=True)
        game.dinosaurs.append(Dinosaur(x, y, aggressive=True))

    logger.info(f"Spawned {n_normal} normal and {n_aggressive} aggressive dinosaurs.")

def spawn_lava(game: Game, count: int = 8, radius: int = 30) -> list[tuple[int, int]]:
    """
    Spawn lava near the center of the map, damaging the player on contact.
    """
    cx = Config.MAP_WIDTH // 2
    cy = Config.MAP_HEIGHT // 2
    lava_positions = []
    for _ in range(count):
        rx = cx + random.randint(-radius, radius)
        ry = cy + random.randint(-radius, radius)
        if 0 <= rx < Config.MAP_WIDTH and 0 <= ry < Config.MAP_HEIGHT:
            # Only spawn on passable tiles
            if Config.BIOMES[game.game_map[ry][rx]]["passable"]:
                lava_positions.append((rx, ry))
    logger.info(f"Lava spawned at positions: {lava_positions}")
    return lava_positions
