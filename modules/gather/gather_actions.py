import pydirectinput
import time
import random
from capture.dxcam_capture import DXCamCapture
class GatherActions:
    def __init__(self):
        pydirectinput.PAUSE = 0.01
        pydirectinput.FAILSAFE = False
        self.screen_center = DXCamCapture().get_screen_center()
        pass
    @staticmethod

    def press_key(key, duration=0.05):
        pydirectinput.keyDown(key)
        time.sleep(duration)
        pydirectinput.keyUp(key)

    def release_xiaoyin_qianlang(self):
        self.press_key('2')
        time.sleep(1.2)
        self.press_key('e')

    def open_map(self):
        self.press_key('m')

    def enable_auto_pathfinding(self):
        self.press_key('n', 2)

    def dismount(self):
        self.press_key('q')

    def start_patrol(self):
        self.press_key('a', 3)
        time.sleep(random.uniform(1, 2))
        self.press_key('s', 3)
        time.sleep(random.uniform(1, 2))
        self.press_key('d', 3)
        time.sleep(random.uniform(1, 2))
        self.press_key('w', 3)
        time.sleep(random.uniform(1, 2))

    def drag_mouse_up(self, distance: int = 300, base_duration: float = 10):
        start_x, start_y = pydirectinput.position()

        offset_x = random.randint(0, 40)
        end_x = start_x + offset_x
        end_y = start_y - distance
        duration = random.uniform(base_duration * 0.9, base_duration * 1.1)

        pydirectinput.mouseDown(button="left")
        pydirectinput.moveTo(end_x, end_y, duration=duration)
        pydirectinput.mouseUp(button="left")

    def press_space_key(self):
        self.press_key('space')

    def press_esc_key(self):
        self.press_key('esc')

    def move_to_and_click(
            self,
            x: int,
            y: int,
            duration: float = 0.2,
            button: str = "left",
            click_interval: float = 0.05,
    ):
        pydirectinput.moveTo(x, y, duration=duration)
        time.sleep(click_interval)
        pydirectinput.click(x=x, y=y, button=button)

    def drag_map_point_back_to_target(
            self,
            target_pos: tuple[int, int],
            duration: float = 0.4,
            button: str = "left",
    ):
        (center_x, center_y) = self.screen_center
        target_x, target_y = target_pos

        # 传送点需要从中心移动到目标位置的位移
        point_offset_x = target_x - center_x
        point_offset_y = target_y - center_y

        # 默认按“鼠标拖动方向 = 地图点移动方向”处理
        drag_dx = point_offset_x
        drag_dy = point_offset_y

        start_x = center_x
        start_y = center_y
        end_x = start_x + drag_dx
        end_y = start_y + drag_dy

        pydirectinput.moveTo(start_x+200, start_y+200, duration=0.1)
        time.sleep(0.05)

        pydirectinput.mouseDown(button=button)
        pydirectinput.moveTo(end_x+200, end_y+200, duration=duration)
        pydirectinput.mouseUp(button=button)

    def press_special_skill_key(self):
        self.press_key('`')
    def press_z_key(self):
        self.press_key('z')
    def press_q_key(self):
        self.press_key('q')
    def press_f_key(self):
        self.press_key('f')
    def reset_position(self):
        self.press_key('s', 1)
        self.press_key('w')

    def move_screen(self, distance: int = 100, base_duration: float = 20):
        start_x, start_y = pydirectinput.position()
        end_x = start_x
        end_y = start_y + distance
        print(end_x, end_y)
        duration = random.uniform(base_duration * 0.9, base_duration * 1.1)
        pydirectinput.mouseDown(button="right")
        pydirectinput.moveTo(end_x, end_y, duration=duration)
        pydirectinput.mouseUp(button="right")

if __name__ == "__main__":
    actions = GatherActions()
    actions.press_special_skill_key()