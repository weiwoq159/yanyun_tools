import pydirectinput
import time
from capture.dxcam_capture import DXCamCapture


def press_key(key, duration=0.05):
    pydirectinput.keyDown(key)
    time.sleep(duration)
    pydirectinput.keyUp(key)


class FengshaActions:
    def __init__(self):
        pydirectinput.PAUSE = 0.01
        pydirectinput.FAILSAFE = False
        self.screen_center = DXCamCapture().get_screen_center()
        pass

    def press_f_key(self, key, duration=0.05):
        press_key('f', duration)