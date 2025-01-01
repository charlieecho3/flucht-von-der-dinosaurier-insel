# joystick_handler.py

import pygame
import logging
from config import Config

logger = logging.getLogger(__name__)

class JoystickHandler:
    """
    Handles joystick initialization and event processing for movement & actions.
    """

    def __init__(self) -> None:
        pygame.joystick.init()
        self.joystick = None
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False
        self.initialize_joystick()

    def initialize_joystick(self) -> None:
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            logger.info("No joysticks detected.")
            return
        try:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            logger.info(f"Joystick '{self.joystick.get_name()}' initialized.")
        except pygame.error as e:
            logger.warning(f"Failed to initialize joystick: {e}")
            self.joystick = None

    def process_events(self, events: list[pygame.event.Event]) -> list[str]:
        """
        Process joystick events, update movement flags, return a list of actions.
        """
        actions = []
        if not self.joystick:
            return actions

        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == Config.JOYSTICK_FIRE_BUTTON:
                    actions.append('activate_repellent')
            elif event.type == pygame.JOYAXISMOTION:
                axis_0 = self.joystick.get_axis(0)
                if axis_0 < -Config.JOYSTICK_AXIS_THRESHOLD:
                    self.move_left = True
                    self.move_right = False
                elif axis_0 > Config.JOYSTICK_AXIS_THRESHOLD:
                    self.move_right = True
                    self.move_left = False
                else:
                    self.move_left = False
                    self.move_right = False

                axis_1 = self.joystick.get_axis(1)
                if axis_1 < -Config.JOYSTICK_AXIS_THRESHOLD:
                    self.move_up = True
                    self.move_down = False
                elif axis_1 > Config.JOYSTICK_AXIS_THRESHOLD:
                    self.move_down = True
                    self.move_up = False
                else:
                    self.move_up = False
                    self.move_down = False

        return actions

    def get_movement(self) -> tuple[int, int]:
        """
        Return movement directions as (dx, dy) in {-1, 0, +1}.
        """
        dx = 0
        dy = 0
        if self.move_left:
            dx -= 1
        if self.move_right:
            dx += 1
        if self.move_up:
            dy -= 1
        if self.move_down:
            dy += 1
        return dx, dy

    def quit(self) -> None:
        """
        Clean up joystick resources.
        """
        if self.joystick:
            logger.info(f"Joystick '{self.joystick.get_name()}' has been quit.")
            self.joystick.quit()
        pygame.joystick.quit()
