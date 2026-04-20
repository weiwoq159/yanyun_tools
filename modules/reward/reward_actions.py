import time
from typing import Optional, Tuple

import pydirectinput
from capture.window_finder import WindowFinder


class RewardActions:
    def __init__(self):
        self.finder = WindowFinder()
        self.rect = self.finder.get_window_rect()
        pydirectinput.PAUSE = 0.02
        pydirectinput.FAILSAFE = False

    @staticmethod
    def click_item(point: Tuple[int, int]) -> None:
        pydirectinput.moveTo(point[0], point[1])
        time.sleep(0.1)
        pydirectinput.click()
    def press_refresh_key(self):
        pydirectinput.keyDown('r')
        time.sleep(0.08)
        pydirectinput.keyUp("r")

    def press_space_key(self):
        pydirectinput.keyDown('space')
        time.sleep(0.08)
        pydirectinput.keyUp("space")
    def press_esc_key(self):
        pydirectinput.press("esc")