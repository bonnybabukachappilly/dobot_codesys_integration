from threading import Thread
from time import sleep
from typing import Callable

from .panel import TVPanelMechanism
from .screen import TVScreenMechanism
from .rim import TVRimMechanism


panel_mech = TVPanelMechanism()
rim_mech = TVRimMechanism()
screen_mech = TVScreenMechanism()

delay_time = 0.6


def multiple_delayed_thread(items: list[Callable]) -> None:
    th: list[Thread] = []

    for item in items:
        _th = Thread(target=item, daemon=True)
        _th.start()
        th.append(_th)

        sleep(delay_time)

    for _th in th:
        _th.join()


def move_to_passive() -> None:
    multiple_delayed_thread([
        panel_mech.move_passive,
        rim_mech.move_passive,
        screen_mech.move_passive
    ])


def move_to_active() -> None:
    multiple_delayed_thread([
        panel_mech.move_active,
        rim_mech.move_active,
        screen_mech.move_active
    ])


def reset() -> None:
    panel_mech.reset_parts()
    rim_mech.reset_parts()
    screen_mech.reset_parts()


def create() -> None:
    panel_mech.create_parts()
    rim_mech.create_parts()
    screen_mech.create_parts()
