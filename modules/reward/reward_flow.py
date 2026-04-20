import time
from dataclasses import dataclass
from datetime import datetime

from capture.dxcam_capture import DXCamCapture
from modules.reward.reward_actions import RewardActions
from modules.reward.reward_detector import RewardDetector
from config.settings import HEALING_THRESHOLD
from config.regions import (RIGHT_REWARD_ACCEPT_REGION, LEFT_CARD_SEARCH_REGION)

@dataclass
class FlowResult:
    success: bool
    state: str
    message: str = ""
    elapsed: float = 0.0


class RewardFlow:
    def __init__(self):
        self.dxcam_capture = DXCamCapture()
        self.reward_detector = RewardDetector()
        self.reward_actions = RewardActions()

        # 等待相关
        self.refresh_wait = 0.5          # 按 R 后等列表刷新
        self.detail_wait = 0.3           # 检测到右侧详情后，按空格前稍等一下
        self.check_interval = 0.2        # 轮询检测间隔（目前仅作为可配置参数保留）
        self.enter_world_timeout = 3.0   # 进入世界页最多等 3 秒

        # 阈值
        self.healing_threshold = HEALING_THRESHOLD
        self.claim_threshold = HEALING_THRESHOLD
        self.expired_threshold = HEALING_THRESHOLD
        self.enter_world_threshold = HEALING_THRESHOLD

    # =========================
    # 通用日志/计时工具
    # =========================
    def _now_str(self) -> str:
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def _log(self, step: str, message: str, start_at: float | None = None):
        if start_at is None:
            print(f"[{self._now_str()}] [{step}] {message}")
        else:
            elapsed = time.perf_counter() - start_at
            print(f"[{self._now_str()}] [{step}] {message} | 耗时: {elapsed:.3f}s")

    def _build_result(self, success: bool, state: str, message: str, start_at: float) -> FlowResult:
        total_elapsed = time.perf_counter() - start_at
        return FlowResult(
            success=success,
            state=state,
            message=f"{message} | 本轮总耗时: {total_elapsed:.3f}s",
            elapsed=total_elapsed,
        )

    # =========================
    # 主流程
    # =========================
    def run_once(self) -> FlowResult:
        total_start = time.perf_counter()
        self._log("RUN_ONCE", "开始执行单轮悬赏流程")

        # STEP 1: 全屏截图
        step_start = time.perf_counter()
        image = self.dxcam_capture.capture_fullscreen()
        if image is None:
            self._log("STEP1", "全屏截图失败", step_start)
            return self._build_result(False, "capture_failed", "截图失败", total_start)
        self._log("STEP1", "全屏截图成功", step_start)

        # STEP 2: 判断是否在悬赏页面
        step_start = time.perf_counter()
        is_reward_page = self.reward_detector.is_reward_page(image)
        if not is_reward_page:
            self._log("STEP2", "当前不在悬赏页面", step_start)
            return self._build_result(False, "not_reward_page", "当前不在悬赏页面", total_start)
        self._log("STEP2", "当前页面识别为悬赏页面", step_start)

        # STEP 3: 刷新直到找到治疗悬赏
        step_start = time.perf_counter()
        healing_match = self._refresh_until_healing_card()
        if not healing_match:
            self._log("STEP3", "长时间未刷到治疗悬赏", step_start)
            return self._build_result(False, "healing_not_found", "长时间未刷到治疗悬赏", total_start)
        self._log(
            "STEP3",
            f"找到治疗悬赏 center={healing_match.get('center')} score={healing_match.get('score', 0.0):.3f}",
            step_start
        )

        # STEP 4: 点击治疗悬赏
        step_start = time.perf_counter()
        cx, cy = healing_match["center"]

        click_point = (
            cx + LEFT_CARD_SEARCH_REGION["x1"],
            cy + LEFT_CARD_SEARCH_REGION["y1"],
        )
        self.reward_actions.click_item(click_point)
        self._log("STEP4", f"已点击治疗悬赏 center={healing_match['center']}", step_start)

        # STEP 5: 等待右侧详情出现
        step_start = time.perf_counter()
        detail_result = self._wait_until_healing_detail_card()
        if not detail_result.success:
            self._log("STEP5", f"等待右侧详情失败: {detail_result.message}", step_start)
            return self._build_result(False, detail_result.state, detail_result.message, total_start)
        self._log("STEP5", f"右侧详情出现: {detail_result.message}", step_start)

        # STEP 6: 按空格接取
        step_start = time.perf_counter()
        self.reward_actions.press_space_key()
        self._log("STEP6", "已按 SPACE 接取悬赏", step_start)

        # STEP 7: 等待进入世界 / 悬赏失效
        step_start = time.perf_counter()
        enter_result = self._wait_until_enter_world_card()
        self._log("STEP7", enter_result.message, step_start)

        return self._build_result(
            enter_result.success,
            enter_result.state,
            enter_result.message,
            total_start
        )

    def run_loop(self, max_round: int = 100) -> FlowResult:
        loop_total_start = time.perf_counter()
        self._log("RUN_LOOP", f"开始循环执行，最多 {max_round} 轮")

        for i in range(max_round):
            round_no = i + 1
            round_start = time.perf_counter()
            self._log("LOOP", f"开始第 {round_no} 轮")

            result = self.run_once()

            self._log(
                "LOOP",
                f"第 {round_no} 轮结束 -> success={result.success}, state={result.state}, message={result.message}",
                round_start
            )

            if result.success:
                total_elapsed = time.perf_counter() - loop_total_start
                self._log("RUN_LOOP", f"流程成功结束，总耗时 {total_elapsed:.3f}s")
                return FlowResult(
                    True,
                    result.state,
                    f"第 {round_no} 轮成功: {result.message} | run_loop总耗时: {total_elapsed:.3f}s",
                    total_elapsed
                )

            if result.state in ("reward_expired", "enter_world_timeout_esc"):
                self._log("LOOP", f"第 {round_no} 轮未成功，准备重新开始")
                time.sleep(0.5)
                continue

            total_elapsed = time.perf_counter() - loop_total_start
            self._log("RUN_LOOP", f"流程提前失败，总耗时 {total_elapsed:.3f}s")
            return FlowResult(
                False,
                result.state,
                f"第 {round_no} 轮失败: {result.message} | run_loop总耗时: {total_elapsed:.3f}s",
                total_elapsed
            )

        total_elapsed = time.perf_counter() - loop_total_start
        self._log("RUN_LOOP", f"超过最大轮数 {max_round}，流程结束，总耗时 {total_elapsed:.3f}s")
        return FlowResult(
            False,
            "loop_exceeded",
            f"超过最大轮数 {max_round}，流程结束 | run_loop总耗时: {total_elapsed:.3f}s",
            total_elapsed
        )

    # =========================
    # 子步骤
    # =========================
    def _wait_until_enter_world_card(self) -> FlowResult:
        """
        3 秒内等待两种状态：
        1. enter_world -> 按 space
        2. expired -> 按 esc

        如果 3 秒内仍未检测到 enter_world，也按 esc 退出
        """
        wait_start = time.perf_counter()
        start_time = time.monotonic()
        check_count = 0

        self._log("WAIT_ENTER_WORLD", f"开始等待进入世界页面，超时时间 {self.enter_world_timeout:.1f}s")

        while time.monotonic() - start_time < self.enter_world_timeout:
            check_count += 1
            loop_start = time.perf_counter()

            # 1. 截图
            capture_start = time.perf_counter()
            image = self.dxcam_capture.capture_fullscreen()
            if image is None:
                self._log("WAIT_ENTER_WORLD", f"第{check_count}次检测截图失败", loop_start)
                continue
            self._log("WAIT_ENTER_WORLD_CAPTURE", f"第{check_count}次全屏截图成功", capture_start)

            # 2. 模板匹配
            match_start = time.perf_counter()
            enter_world_match = self.reward_detector.match_template_best(image, "enter_world")
            expired_match = self.reward_detector.match_template_best(image, "expired")

            enter_world_score = enter_world_match.get("score", 0.0) if enter_world_match else 0.0
            expired_score = expired_match.get("score", 0.0) if expired_match else 0.0

            enter_world_ok = enter_world_score >= self.enter_world_threshold
            expired_ok = expired_score >= self.expired_threshold

            self._log(
                "WAIT_ENTER_WORLD_MATCH",
                f"第{check_count}次匹配完成 enter_world={enter_world_score:.3f}, expired={expired_score:.3f}",
                match_start
            )

            # 3. 状态判断
            if expired_ok and (not enter_world_ok or expired_score >= enter_world_score):
                action_start = time.perf_counter()
                self.reward_actions.press_esc_key()
                self._log("WAIT_ENTER_WORLD_ACTION", f"第{check_count}次检测到悬赏失效，已按 ESC", action_start)
                return FlowResult(
                    False,
                    "reward_expired",
                    f"第{check_count}次检测到悬赏失效，score={expired_score:.3f}，已按 ESC | wait耗时: {time.perf_counter() - wait_start:.3f}s",
                    time.perf_counter() - wait_start
                )

            if enter_world_ok:
                action_start = time.perf_counter()
                self.reward_actions.press_space_key()
                self._log("WAIT_ENTER_WORLD_ACTION", f"第{check_count}次检测到进入世界页面，已按 SPACE", action_start)
                return FlowResult(
                    True,
                    "enter_world_found",
                    f"第{check_count}次检测到进入世界页面，score={enter_world_score:.3f}，已按 SPACE | wait耗时: {time.perf_counter() - wait_start:.3f}s",
                    time.perf_counter() - wait_start
                )

            self._log("WAIT_ENTER_WORLD", f"第{check_count}次未命中目标状态，继续轮询", loop_start)

        # 超时按 ESC
        action_start = time.perf_counter()
        self.reward_actions.press_esc_key()
        self._log("WAIT_ENTER_WORLD_ACTION", "等待超时，已按 ESC", action_start)
        return FlowResult(
            False,
            "enter_world_timeout_esc",
            f"{self.enter_world_timeout:.1f}秒内未检测到进入世界页面，已按 ESC 退出 | wait耗时: {time.perf_counter() - wait_start:.3f}s",
            time.perf_counter() - wait_start
        )

    def _wait_until_healing_detail_card(self, max_check: int = 20) -> FlowResult:
        wait_start = time.perf_counter()
        self._log("WAIT_DETAIL", f"开始等待右侧接取详情，最多检测 {max_check} 次")

        for i in range(max_check):
            check_no = i + 1
            check_start = time.perf_counter()

            # 1. 截图右侧区域
            capture_start = time.perf_counter()
            image = self.dxcam_capture.capture_game_region(RIGHT_REWARD_ACCEPT_REGION)
            if image is None:
                self._log("WAIT_DETAIL", f"第{check_no}次右侧区域截图失败", check_start)
                continue
            self._log("WAIT_DETAIL_CAPTURE", f"第{check_no}次右侧区域截图成功", capture_start)

            # 2. 匹配 claim
            match_start = time.perf_counter()
            claim_match = self.reward_detector.match_template_best(image, "claim")
            score = claim_match.get("score", 0.0) if claim_match else 0.0
            self._log("WAIT_DETAIL_MATCH", f"第{check_no}次匹配完成 score={score:.3f}", match_start)

            if score >= self.claim_threshold:
                self._log("WAIT_DETAIL", f"第{check_no}次检测到接取悬赏详情", check_start)
                return FlowResult(
                    True,
                    "claim_found",
                    f"第{check_no}次检测到接取悬赏详情，score={score:.3f} | wait耗时: {time.perf_counter() - wait_start:.3f}s",
                    time.perf_counter() - wait_start
                )

            self._log("WAIT_DETAIL", f"第{check_no}次未检测到接取详情", check_start)

        return FlowResult(
            False,
            "claim_not_found",
            f"等待超时，右侧未出现接取悬赏详情 | wait耗时: {time.perf_counter() - wait_start:.3f}s",
            time.perf_counter() - wait_start
        )

    def _refresh_until_healing_card(self, max_refresh: int = 100):
        refresh_total_start = time.perf_counter()
        self._log("REFRESH", f"开始刷新治疗悬赏，最多 {max_refresh} 次")

        for i in range(max_refresh):
            refresh_no = i + 1
            refresh_start = time.perf_counter()

            # 1. 按 R
            action_start = time.perf_counter()
            self.reward_actions.press_refresh_key()
            self._log("REFRESH_ACTION", f"第{refresh_no}次已按 R", action_start)

            # 2. 等刷新
            sleep_start = time.perf_counter()
            time.sleep(self.refresh_wait)
            self._log("REFRESH_SLEEP", f"第{refresh_no}次等待列表刷新", sleep_start)

            # 3. 全屏截图
            capture_start = time.perf_counter()
            # image = self.dxcam_capture.capture_fullscreen()
            image = self.dxcam_capture.capture_game_region(LEFT_CARD_SEARCH_REGION)
            if image is None:
                self._log("REFRESH", f"第{refresh_no}次刷新截图失败，继续刷新", refresh_start)
                continue
            self._log("REFRESH_CAPTURE", f"第{refresh_no}次全屏截图成功", capture_start)

            # 4. 匹配治疗悬赏
            match_start = time.perf_counter()
            healing_match = self.reward_detector.match_template_best(image, "healing_card")
            score = healing_match.get("score", 0.0) if healing_match else 0.0
            self._log("REFRESH_MATCH", f"第{refresh_no}次匹配完成 score={score:.3f}", match_start)

            if score >= self.healing_threshold:
                self._log(
                    "REFRESH",
                    f"第{refresh_no}次刷新刷到治疗悬赏，center={healing_match.get('center')}，score={score:.3f}",
                    refresh_start
                )
                self._log("REFRESH", f"刷新阶段总耗时 {time.perf_counter() - refresh_total_start:.3f}s")
                return healing_match

            self._log(
                "REFRESH",
                f"第{refresh_no}次刷新未刷到治疗悬赏，score={score:.3f}，继续刷新",
                refresh_start
            )

        self._log("REFRESH", f"刷新结束，未找到治疗悬赏，总耗时 {time.perf_counter() - refresh_total_start:.3f}s")
        return None


if __name__ == "__main__":
    reward_flow = RewardFlow()
    result = reward_flow.run_loop()
    print("\n========== FINAL RESULT ==========")
    print(result)