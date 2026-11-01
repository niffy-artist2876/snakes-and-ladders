"""Run with python -m snakes_ladders.main."""

import logging

import pygame
from time import perf_counter

from snakes_ladders.controller.game_controller import GameController
from snakes_ladders.ui.game_screen import GameScreen
from snakes_ladders.ui.result_screen import ResultScreen
from snakes_ladders.ui.setup_screen import SetupScreen
from snakes_ladders.ui.viewport import LOGICAL_SIZE, logical_event, present, viewport_rect
from snakes_ladders.ui.animation import TARGET_FPS
from snakes_ladders.ui.frame_pacing import FramePacer

logger = logging.getLogger("snakes_ladders.rendering")


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

        screens = {
            "setup": make_setup(),
            "game": GameScreen(controller),
            "result": ResultScreen(controller),
        }
        pacer = FramePacer(TARGET_FPS)
        force_redraw = True
        last_flip = perf_counter()
        last_wait = 0.0
        while controller.running:
            seconds = pacer.begin_frame()
            started = perf_counter()
            animation_at_frame_start = screens["game"].animation
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    controller.running = False
                elif event.type == pygame.VIDEORESIZE:
                    size = (max(LOGICAL_SIZE[0], event.w), max(LOGICAL_SIZE[1], event.h))
                    surface = pygame.display.set_mode(size, pygame.RESIZABLE)
                    force_redraw = True
                elif event.type == pygame.WINDOWEXPOSED:
                    force_redraw = True
                else:
                    event = logical_event(event, viewport_rect(surface.get_size()))
                    if event is None:
                        continue
                    previous_screen = controller.screen
                    screens[controller.screen].handle_event(event)
                    if previous_screen != "setup" and controller.screen == "setup":
                        screens["setup"] = make_setup()
            events_done = perf_counter()
            if (controller.screen == "game"
                    and screens["game"].animation is animation_at_frame_start):
                # A move started by this frame's input must not consume time
                # spent sleeping on the idle screen before that input.
                screens["game"].update(seconds)
            update_done = perf_counter()
            dirty = screens[controller.screen].draw(canvas)
            draw_done = perf_counter()
            present(canvas, surface, None if force_redraw else dirty)
            force_redraw = False
            present_done = perf_counter()
            pygame.display.flip()
            flipped = perf_counter()
            if controller.screen == "game":
                screens["game"].record_frame(flipped)
                if flipped - last_flip > 1 / 30:
                    logger.warning(
                        "Slow frame: interval=%.2fms events=%.2fms update=%.2fms "
                        "draw=%.2fms present=%.2fms flip=%.2fms previous_wait=%.2fms driver=%s",
                        (flipped-last_flip)*1000, (events_done-started)*1000,
                        (update_done-events_done)*1000, (draw_done-update_done)*1000,
                        (present_done-draw_done)*1000, (flipped-present_done)*1000,
                        last_wait*1000, pygame.display.get_driver())
            last_flip = flipped
            wait_started = perf_counter()
            animating = controller.screen == "game" and screens["game"].animation is not None
            pacer.wait(precise=animating)
            last_wait = perf_counter() - wait_started
    finally:
        pygame.quit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
