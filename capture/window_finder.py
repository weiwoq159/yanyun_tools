import time
from typing import Dict, Optional

import pygetwindow as gw

from config.settings import (
    WINDOW_TITLE_KEYWORD,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
)


class WindowFinder:
    def __init__(
        self,
        keyword: str = WINDOW_TITLE_KEYWORD,
        min_width: int = MIN_WINDOW_WIDTH,
        min_height: int = MIN_WINDOW_HEIGHT,
        auto_init: bool = True,
    ):
        self.keyword = keyword
        self.min_width = min_width
        self.min_height = min_height

        self.window = None
        self.rect = None
        self.center = None

        if auto_init:
            self.refresh()

    def refresh(self, keyword: Optional[str] = None) -> Optional[gw.Win32Window]:
        """
        刷新窗口对象、矩形信息、中心点
        找不到时不抛异常，返回 None
        """
        self.window = self.find_game_window(keyword)
        self.rect = self.get_window_rect()
        self.center = self.get_window_center()
        return self.window

    def find_game_window(self, keyword: Optional[str] = None) -> Optional[gw.Win32Window]:
        """
        根据窗口标题关键字查找游戏窗口
        """
        target_keyword = keyword or self.keyword

        windows = gw.getWindowsWithTitle(target_keyword)
        windows = [
            w for w in windows
            if w.width >= self.min_width and w.height >= self.min_height
        ]

        if not windows:
            return None

        return windows[0]

    def get_window_rect(self) -> Optional[Dict[str, int]]:
        """
        获取窗口矩形信息
        """
        if self.window is None:
            return None

        return {
            "left": self.window.left,
            "top": self.window.top,
            "width": self.window.width,
            "height": self.window.height,
            "right": self.window.left + self.window.width,
            "bottom": self.window.top + self.window.height,
        }

    def get_window_center(self) -> Optional[Dict[str, int]]:
        """
        获取窗口中心点
        """
        if self.rect is None:
            return None

        return {
            "x": self.rect["left"] + self.rect["width"] // 2,
            "y": self.rect["top"] + self.rect["height"] // 2,
        }

    def is_window_minimized(self) -> bool:
        """
        判断窗口是否最小化
        """
        if self.window is None:
            return False

        try:
            return self.window.isMinimized
        except Exception:
            return False

    def activate_window(self, wait: float = 0.2) -> bool:
        """
        尝试激活窗口
        """
        if self.window is None:
            return False

        try:
            if self.is_window_minimized():
                self.window.restore()
                time.sleep(wait)

            self.window.activate()
            time.sleep(wait)
            return True
        except Exception as e:
            print(f"[WINDOW] 激活窗口失败: {e}")
            return False

    def print_window_info(self) -> None:
        """
        打印窗口信息
        """
        if self.window is None or self.rect is None or self.center is None:
            print(f"[WINDOW] 未找到窗口: keyword={self.keyword}")
            return

        print(
            f"[WINDOW] title={self.window.title} "
            f"left={self.rect['left']} top={self.rect['top']} "
            f"width={self.rect['width']} height={self.rect['height']} "
            f"center=({self.center['x']},{self.center['y']}) "
            f"minimized={self.is_window_minimized()}"
        )

    def ensure_window_ready(
        self,
        keyword: Optional[str] = None,
        auto_activate: bool = False,
        strict: bool = True,
    ) -> Optional[gw.Win32Window]:
        """
        刷新并校验窗口是否可用
        strict=True: 找不到直接抛异常
        strict=False: 找不到返回 None
        """
        self.refresh(keyword)

        if self.window is None:
            if strict:
                raise RuntimeError(f"未找到游戏窗口，关键字: {keyword or self.keyword}")
            return None

        if self.window.width < self.min_width or self.window.height < self.min_height:
            if strict:
                raise RuntimeError(
                    f"找到窗口但尺寸异常: width={self.window.width}, height={self.window.height}"
                )
            return None

        if auto_activate:
            self.activate_window()

        return self.window

    def get_relative_region(self, region: Dict[str, int]) -> Optional[Dict[str, int]]:
        """
        将相对游戏窗口的区域，转换为屏幕绝对区域
        """
        if self.rect is None:
            return None

        left = self.rect["left"] + region["x1"]
        top = self.rect["top"] + region["y1"]
        width = region["x2"] - region["x1"]
        height = region["y2"] - region["y1"]

        return {
            "left": left,
            "top": top,
            "width": width,
            "height": height,
        }


if __name__ == "__main__":
    finder = WindowFinder(auto_init=True)

    # 调试阶段：找不到别炸
    finder.ensure_window_ready(auto_activate=False, strict=False)
    finder.print_window_info()



