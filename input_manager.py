# input_manager.py

from __future__ import annotations  # Enables postponed evaluation of annotations
import pygame
import logging
from state import GameState
from typing import TYPE_CHECKING

from config import Config  # Import Config to use in type annotations and logic

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game import Game  # Imported only for type checking to avoid circular imports

def handle_state_event(game: Game, event: pygame.event.Event) -> None:
    """
    Dispatch incoming events based on the current game state.
    
    Args:
        game (Game): The main game instance.
        event (pygame.event.Event): The event to handle.
    """
    if game.state == GameState.MAIN_MENU:
        game.title_screen.handle_event(event, game)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game.state = GameState.INTRO
                game.reset_game()
                logger.info("Transitioned to INTRO state from MAIN_MENU.")
            elif event.key == pygame.K_h:
                game.state = GameState.HELP
                logger.info("Transitioned to HELP state from MAIN_MENU.")
            elif event.key == pygame.K_q:
                game.running = False
                logger.info("Exiting game from MAIN_MENU.")

    elif game.state == GameState.INTRO:
        game.intro_screen.handle_event(event, game)
        if event.type == pygame.KEYDOWN:
            game.state = GameState.PLAYING
            logger.info("Transitioned to PLAYING state from INTRO.")

    elif game.state == GameState.HELP:
        game.help_screen.handle_event(event, game)
        if event.type == pygame.KEYDOWN:
            game.state = GameState.MAIN_MENU
            game.reset_game()
            logger.info("Returned to MAIN_MENU from HELP.")

    elif game.state == GameState.PAUSE:
        game.pause_screen.handle_event(event, game)

    elif game.state == GameState.GAME_OVER:
        game.lose_screen.handle_event(event, game)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            game.state = GameState.MAIN_MENU
            game.reset_game()
            logger.info("Returned to MAIN_MENU from GAME_OVER.")

    elif game.state == GameState.WON:
        game.win_screen.handle_event(event, game)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            game.state = GameState.MAIN_MENU
            game.reset_game()
            logger.info("Returned to MAIN_MENU from WON.")

    elif game.state == GameState.PLAYING:
        handle_events_playing(game, event)

def handle_events_playing(game: Game, event: pygame.event.Event) -> None:
    """
    Process keyboard/joystick events while in the PLAYING state.
    
    Args:
        game (Game): The main game instance.
        event (pygame.event.Event): The event to handle.
    """
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            game.state = GameState.PAUSE
            logger.info("Paused game from PLAYING state.")
        elif event.key == pygame.K_SPACE:
            if game.player.inventory.get("repellent", 0) > 0:
                game.player.trigger_repellent()
                game.hud.trigger_flash((0, 0, 255), 100, 0.2)
                logger.info("Player activated repellent using SPACE key.")
            else:
                logger.info("Player attempted to activate repellent but none are available.")
        elif event.key in [pygame.K_e, pygame.K_RSHIFT]:
            if game.player.inventory.get("potion", 0) > 0 and game.player.hp < Config.PLAYER_MAX_HP:
                game.player.use_potion()
                game.hud.trigger_flash((0, 255, 0), 100, 0.2)
                logger.info("Player used potion with key press.")
            else:
                if game.player.inventory.get("potion", 0) <= 0:
                    logger.info("Player attempted to use potion but none are available.")
                if game.player.hp >= Config.PLAYER_MAX_HP:
                    logger.info("Player attempted to use potion but HP is already full.")
