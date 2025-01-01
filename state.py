# state.py

from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = auto()
    INTRO = auto()
    HELP = auto()
    PAUSE = auto()
    GAME_OVER = auto()
    WON = auto()
    PLAYING = auto()
