import pygetwindow as gw

from capture.window_finder import WindowFinder
from config.settings import WINDOW_TITLE_KEYWORD


def print_all_windows():
    print("==== 当前系统窗口列表 ====")
    for w in gw.getAllWindows():
        title = (w.title or "").strip()
        if not title:
            continue
        print(
            f"title={title} | left={w.left} top={w.top} "
            f"width={w.width} height={w.height}"
        )


def main():
    print_all_windows()

    print("\n==== 查找目标游戏窗口 ====")
    finder = WindowFinder(WINDOW_TITLE_KEYWORD)

    if finder.window is None:
        print("\n[RESULT] 没找到窗口")
    else:
        print("\n[RESULT] 找到窗口了")


if __name__ == "__main__":
    main()