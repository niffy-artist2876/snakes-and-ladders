"""Run with python -m snakes_ladders.main."""

import logging

import pygame

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.ui.animation import TARGET_FPS
from snakes_ladders.ui.frame_pacing import FramePacer
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.result_screen import ResultScreen
from snakes_ladders.ui.setup_screen import SetupScreen
from snakes_ladders.ui.viewport import LOGICAL_SIZE, logical_event, present, viewport_rect

logger = logging.getLogger("snakes_ladders.main")


def main():
    pygame.init()
    try:
        surface = pygame.display.set_mode(LOGICAL_SIZE, pygame.RESIZABLE)
        canvas = pygame.Surface(LOGICAL_SIZE)
        pygame.display.set_caption("Snakes and Ladders")
        pygame.key.start_text_input()
        controller = GameController()

        def make_setup():
            return SetupScreen(
                on_start=controller.start_new_game,
                on_resume=controller.on_resume_requested,
                can_resume=controller.can_resume,
                controller=controller,
            )

        def make_screens():
            return {
                "setup": make_setup(),
                "game": GameScreen(controller),
                "result": ResultScreen(controller),
            }

        screens = make_screens()
        pacer = FramePacer(pygame.time.Clock(), TARGET_FPS)
        seconds = 0.0  # Duration of the previous frame; drives animation.
        while controller.running:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        controller.exit_requested()
                    elif event.type == pygame.VIDEORESIZE:
                        size = (max(LOGICAL_SIZE[0], event.w), max(LOGICAL_SIZE[1], event.h))
                        surface = pygame.display.set_mode(size, pygame.RESIZABLE)
                    else:
                        event = logical_event(event, viewport_rect(surface.get_size()))
                        if event is None:
                            continue
                        previous_screen = controller.screen
                        screens[controller.screen].handle_event(event)
                        if previous_screen != "setup" and controller.screen == "setup":
                            screens["setup"] = make_setup()
                    if not controller.running:
                        break
                screen = screens[controller.screen]
                if hasattr(screen, "update"):
                    screen.update(seconds)
                screen.draw(canvas)
                present(canvas, surface)
                pygame.display.flip()
                seconds = pacer.wait(precise=getattr(screen, "animating", False))
            except Exception:
                logger.exception("Unexpected error in the application loop")
                controller.recover_from_error()
                screens = make_screens()
                seconds = 0.0
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
