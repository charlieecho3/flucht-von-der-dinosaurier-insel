# entities/item.py

import pygame
import logging
from config import Config
from entities.base_entity import Entity
from utils import load_frames
from sound_manager import sound_manager

logger = logging.getLogger(__name__)

class Item(Entity):
    """
    Simple item entity with a type (potion or repellent).
    """
    def __init__(self, x: float, y: float, type_: str) -> None:
        super().__init__(x, y)
        self.type = type_
        self.frames_right, _ = load_frames([type_], "items")
        self.frames = self.frames_right
        self.current_frame = 0

    def update(self, dt: float) -> None:
        pass

    def on_pickup(self) -> None:
        if self.type in ("potion", "repellent"):
            snd = sound_manager.sounds["actions"].get("potion_pickup", None)
            if snd:
                snd.play()

    def get_current_frame(self) -> pygame.Surface:
        if self.frames:
            return self.frames[self.current_frame]
        return pygame.Surface((Config.TILE_SIZE, Config.TILE_SIZE), pygame.SRCALPHA)
