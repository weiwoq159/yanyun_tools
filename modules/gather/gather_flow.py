import time

from capture.dxcam_capture import DXCamCapture
from modules.gather.gather_actions import GatherActions
from modules.gather.gather_detector import GatherDetector
from config.regions import ASSASSINATE_ROI, COLLECT_ITEMS_ROI, SPECIAL_SKILL_ROI


class GatherFlow:
    def __init__(self):
        self.dx = DXCamCapture()
        self.gather_actions = GatherActions()
        self.detector = GatherDetector()
        self.screen_center_x, self.screen_center_y = self.dx.get_screen_center()
        self.open_map_wait = 1
        self.click_wait = 1
        self.esc_wait = 1
        self.drag_wait = 1
        self.auto_pathfinding_wait = 20
        self.dismount_wait = 2
        self.loop_interval = 20

    def _prepare_gather(self):
        self.gather_actions.enable_auto_pathfinding()
        time.sleep(self.auto_pathfinding_wait)

        self.gather_actions.dismount()
        time.sleep(self.dismount_wait)

        self.gather_actions.release_xiaoyin_qianlang()

        for _ in range(2):
            self.gather_actions.start_patrol()

    def _open_map_and_find_stones(self):
        self.gather_actions.open_map()
        time.sleep(self.open_map_wait)

        self.gather_actions.drag_mouse_up()
        time.sleep(self.open_map_wait)

        stone_points = self.detector.find_way_stones()
        if not stone_points:
            print("[GatherFlow] 未找到任何传送锚点")
            return []

        # 如果 detector 里还没排，这里兜底按 x 从大到小排
        stone_points = sorted(stone_points, key=lambda p: p[0], reverse=True)
        print(f"[GatherFlow] 找到锚点数量: {len(stone_points)}")
        return stone_points

    def _try_one_stone(self, x: int, y: int) -> bool:
        print(f"[GatherFlow] 尝试锚点: ({x}, {y})")

        self.gather_actions.move_to_and_click(x, y)
        time.sleep(self.click_wait)

        match_score = self.detector.is_target_way_stone()
        print(f"[GatherFlow] 地名匹配分数: {match_score:.4f}")

        if match_score > 0.9:
            print("[GatherFlow] 命中正确锚点，准备传送")
            self.gather_actions.press_space_key()
            return True

        print("[GatherFlow] 锚点不对，关闭并恢复地图位置")
        self.gather_actions.press_esc_key()
        time.sleep(self.esc_wait)

        self.gather_actions.drag_map_point_back_to_target((x, y))
        time.sleep(self.drag_wait)
        return False

    def gather_monkey_wine(self) -> bool:
        print("[GatherFlow] 开始一轮采集流程")

        self._prepare_gather()
        stone_points = self._open_map_and_find_stones()

        if not stone_points:
            print("[GatherFlow] 本轮结束：没有可尝试的锚点")
            return False

        for x, y in stone_points:
            print(x, y)
            if self._try_one_stone(x, y):
                print("[GatherFlow] 本轮成功")
                return True

        print("[GatherFlow] 本轮结束：未找到正确锚点")
        return False

    def wait_for_f_interaction(self, roi, action_name="交互"):
        """
        持续检测页面直到检测到交互提示，按下 F 键
        :param roi: 传入 ASSASSINATE_ROI 或 COLLECT_ITEMS_ROI
        :param action_name: 日志显示的动作名称
        """
        print(f"[GatherFlow] 开始监测 {action_name} 页面...")

        while True:  # 持续监控页面
            # 调用你之前在 detector 中写的 detect_template 方法
            is_detected, pos = self.detector.detect_template(roi, 'f_template')

            if is_detected:
                print(f"[GatherFlow] 成功匹配 {action_name} 提示 (相似度达标), 执行 [F]")
                self.gather_actions.press_f_key()  # 执行按键操作
                time.sleep(0.5)  # 延时防止指令堆叠
                return True

            # 控制检测频率，避免 CPU 占用过高
            time.sleep(0.1)

    def perform_assassination(self):
        """执行暗杀"""
        print("[GatherFlow] 开始暗杀操作")
        return self.wait_for_f_interaction(ASSASSINATE_ROI, action_name="暗杀")

    def collect_loot(self, count=1):
        """
        自动拾取掉落物
        :param count: 预期拾取的次数，拾取通常需要连续按
        """
        print("[GatherFlow] 开始拾取物品")
        return self.wait_for_f_interaction(COLLECT_ITEMS_ROI, action_name=f"拾取")

    def process_black_stone_lock(self):
        """
        处理黑石锁：检测 F 键提示，并在最大尝试次数后移动屏幕
        """
        max_attempts = 5  # 设置最大尝试次数
        attempts = 0
        print("[GatherFlow] 开始刷黑石锁")
        self.gather_actions.press_z_key()
        time.sleep(2)
        self.gather_actions.press_special_skill_key()
        time.sleep(3)
        self.gather_actions.press_special_skill_key()

        while True:
            # 检测指定模板是否存在
            is_template_found, pos = self.detector.detect_template(SPECIAL_SKILL_ROI, 'special_template')

            if not is_template_found:
                # 如果模板未找到，按 Q 键
                print("[GatherFlow] 未检测到模板，执行按 [Q]")
                for i in range(2):
                    self.gather_actions.press_space_key()
                    time.sleep(0.5)
                self.gather_actions.press_q_key()
                break
            else:
                # 如果模板已找到，继续循环检测
                print("[GatherFlow] 检测到模板，继续监控")
                time.sleep(0.5)  # 控制检查频率，避免 CPU 占用过高

        self.gather_actions.press_q_key()

        # 无限循环，直到成功进行暗杀
        while True:
            if self.perform_assassination():
                break
            attempts += 1
            if attempts >= max_attempts:
                print("[GatherFlow] 尝试次数过多，移动屏幕...")
                self.gather_actions.move_screen()  # 假设 move_screen 是移动屏幕的方法
                attempts = 0  # 重置尝试次数

        while True:
            if self.collect_loot():
                break

        self.gather_actions.reset_position()

if __name__ == "__main__":
    g = GatherFlow()
    # g.gather_actions.move_screen()
    # index = 0
    # while True:
    #     print(f"第{index}次刷取黑石锁")
    #     g.process_black_stone_lock()
    #     index += 1
    #     if index % 10 == 0:
    #         g.gather_actions.move_screen()
    #         print("移动屏幕")
    #     time.sleep(1)
    # points = g._open_map_and_find_stones()
    # print(points)
    # time.sleep(2)
    # g.gather_actions.drag_map_point_back_to_target((1403, 1234))

    # g.gather_actions.drag_map_point_back_to_target()
    while True:
        ok = g.gather_monkey_wine()
        print(f"[GatherFlow] 本轮结果: {'成功' if ok else '失败'}")
        time.sleep(g.loop_interval)