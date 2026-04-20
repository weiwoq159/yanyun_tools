import cv2
import numpy as np
from pathlib import Path

from config.paths import REWARD_TEMPLATE_DIR
from config.settings import HEALING_THRESHOLD

class RewardDetector:
    def __init__(self):
        self.template_map = {}
        self.initialize()
        self.reward_page_threshold = HEALING_THRESHOLD

    def initialize(self):
        base_dir = Path(REWARD_TEMPLATE_DIR)

        self.template_map = {
            "healing_card": cv2.imread(str(base_dir / "reward_healing_card_template.png")),
            "resolve_framing_card": cv2.imread(str(base_dir / "reward_resolve_framing_card_template.png")),
            "enter_world": cv2.imread(str(base_dir / "reward_enter_world_template.png")),
            "claim": cv2.imread(str(base_dir / "reward_claim_template.png")),
            "reward_page_template": cv2.imread(str(base_dir / "reward_page_template.png")),
            "expired": cv2.imread(str(base_dir / "reward_expired_template.png")),
        }

        for name, template in self.template_map.items():
            if template is None:
                raise FileNotFoundError(f"模板加载失败: {name}")

    def get_template(self, template_name: str):
        template = self.template_map.get(template_name)
        if template is None:
            raise ValueError(
                f"不支持的模板名: {template_name}，可选值: {list(self.template_map.keys())}"
            )
        return template

    def match_template_best(
        self,
        search_image,
        template_name: str,
        method=cv2.TM_CCOEFF_NORMED,
    ):
        template = self.get_template(template_name)
        result = cv2.matchTemplate(search_image, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(min_val, max_val, min_loc, max_loc)
        h, w = template.shape[:2]
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        center = (top_left[0] + w // 2, top_left[1] + h // 2)

        return {
            "score": float(max_val),
            "top_left": top_left,
            "bottom_right": bottom_right,
            "center": center,
            "template_size": (w, h),
            "result_map": result,
        }

    def is_reward_page(self, search_image):
        result = self.match_template_best(search_image, "reward_page_template")
        score = result.get("score", 0.0)
        return score > self.reward_page_threshold

if __name__ == "__main__":
    image = cv2.imread(r"D:\work\mq\yanyun_tools\assets\sample_images\reward\test2.png")
    if image is None:
        raise FileNotFoundError("测试图片加载失败")

    detector = RewardDetector()

    healing_card = detector.match_template_best(image, 'healing_card')
    print('healing_card', healing_card)