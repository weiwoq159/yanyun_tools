from typing import Dict, Optional

import cv2
import dxcam
import numpy as np

from capture.window_finder import WindowFinder
from config.regions import LEFT_CARD_SEARCH_REGION
import ctypes

class DXCamCapture:
    _camera = None

    def __init__(self, window_finder: Optional[WindowFinder] = None, output_idx: int = 0):
        self.output_idx = output_idx
        self.window_finder = window_finder or WindowFinder(auto_init=False)

    @classmethod
    def get_camera(cls, output_idx: int = 0):
        """
        获取 dxcam 相机实例（单例）
        """
        if cls._camera is None:
            cls._camera = dxcam.create(output_idx=output_idx)
        return cls._camera

    @staticmethod
    def rgb_to_bgr(img: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """
        dxcam 默认返回 RGB，这里转成 OpenCV 常用的 BGR
        """
        if img is None:
            return None
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    def capture_absolute_region(
        self,
        region: Dict[str, int],
        to_bgr: bool = True,
    ) -> Optional[np.ndarray]:
        """
        截取屏幕绝对区域

        region 示例:
        {
            "left": 100,
            "top": 100,
            "width": 500,
            "height": 300
        }
        """
        camera = self.get_camera(self.output_idx)

        left = region["left"]
        top = region["top"]
        right = left + region["width"]
        bottom = top + region["height"]

        img = camera.grab(region=(left, top, right, bottom))
        if img is None:
            return None

        if to_bgr:
            img = self.rgb_to_bgr(img)

        return img

    def capture_fullscreen(self, to_bgr: bool = True) -> Optional[np.ndarray]:
        """
        截全屏
        """
        camera = self.get_camera(self.output_idx)
        img = camera.grab()

        if img is None:
            return None

        if to_bgr:
            img = self.rgb_to_bgr(img)

        return img

    def capture_game_window(
        self,
        to_bgr: bool = True,
        auto_activate: bool = False,
    ) -> Optional[np.ndarray]:
        """
        截取整个游戏窗口区域
        """
        self.window_finder.refresh()

        if self.window_finder.window is None:
            print("[DXCAM] 未找到游戏窗口")
            return None

        if auto_activate:
            self.window_finder.activate_window()

        region = self.window_finder.rect
        return self.capture_absolute_region(region, to_bgr=to_bgr)

    def capture_game_region(
        self,
        relative_region: Dict[str, int],
        to_bgr: bool = True,
        auto_activate: bool = False,
    ) -> Optional[np.ndarray]:
        """
        截取游戏窗口内某个相对区域

        relative_region 示例:
        {
            "x1": 40,
            "y1": 180,
            "x2": 700,
            "y2": 760,
        }
        """
        self.window_finder.refresh()

        if self.window_finder.window is None:
            print("[DXCAM] 未找到游戏窗口")
            return None

        if auto_activate:
            self.window_finder.activate_window()

        absolute_region = self.window_finder.get_relative_region(relative_region)
        if absolute_region is None:
            print("[DXCAM] 相对区域转换失败")
            return None

        return self.capture_absolute_region(absolute_region, to_bgr=to_bgr)

    @staticmethod
    def save_image(img: Optional[np.ndarray], save_path: str) -> bool:
        """
        保存图片到本地
        """
        if img is None:
            print("[DXCAM] 保存失败，img=None")
            return False

        ok = cv2.imwrite(save_path, img)
        if not ok:
            print(f"[DXCAM] 保存失败: {save_path}")
            return False

        print(f"[DXCAM] 图片已保存: {save_path}")
        return True

    @classmethod
    def release_camera(cls) -> None:
        """
        释放相机实例
        """
        cls._camera = None

    @staticmethod
    def get_screen_size() -> tuple[int, int]:
        """
        动态获取主屏幕分辨率
        返回: (screen_width, screen_height)
        """
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        return screen_width, screen_height

    @classmethod
    def get_screen_center(cls) -> tuple[int, int]:
        """
        动态获取屏幕中心点坐标
        """
        screen_width, screen_height = cls.get_screen_size()
        return screen_width // 2, screen_height // 2

if __name__ == "__main__":
    capture = DXCamCapture()

    img1 = capture.capture_fullscreen()
    capture.save_image(img1, "debug_fullscreen.png")

    img2 = capture.capture_game_window()
    capture.save_image(img2, "debug_game_window.png")

    img3 = capture.capture_game_region(
        LEFT_CARD_SEARCH_REGION
    )
    capture.save_image(img3, "debug_game_region.png")