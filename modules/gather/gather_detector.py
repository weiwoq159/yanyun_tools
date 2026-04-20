from pathlib import Path
from typing import List, Tuple

import cv2
from ultralytics import YOLO

from capture.dxcam_capture import DXCamCapture
from config.paths import BASE_DIR
from config.regions import RIGHT_LOCATION_NAME_REGION, ASSASSINATE_ROI, COLLECT_ITEMS_ROI


class GatherDetector:
    def __init__(self):
        self.dx = DXCamCapture()

        self.model_path = BASE_DIR / "train" / "best.pt"
        self.area_template_path = BASE_DIR / "assets" / "templates" / "area_template.png"

        self.model = YOLO(str(self.model_path))
        self.area_template = cv2.imread(str(self.area_template_path))

        if self.area_template is None:
            raise RuntimeError(f"区域模板加载失败: {self.area_template_path}")

        self.area_template_gray = cv2.cvtColor(self.area_template, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def show_detect_boxes(result, boxes, image, window_name: str = "detect_result"):
        if boxes is None or len(boxes) == 0:
            print("未检测到任何目标。")
            cv2.imshow(window_name, image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return

        draw_image = image.copy()

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            class_name = result.names.get(cls_id, str(cls_id))
            label = f"{class_name} {conf:.2f}"

            cv2.rectangle(draw_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

            (text_w, text_h), baseline = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                2,
            )

            text_bg_x1 = x1
            text_bg_y1 = max(0, y1 - text_h - baseline - 6)
            text_bg_x2 = x1 + text_w + 6
            text_bg_y2 = y1

            cv2.rectangle(
                draw_image,
                (text_bg_x1, text_bg_y1),
                (text_bg_x2, text_bg_y2),
                (0, 0, 255),
                -1,
            )

            cv2.putText(
                draw_image,
                label,
                (x1 + 3, y1 - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

            print(
                f"检测到: class={class_name}, conf={conf:.3f}, "
                f"box=({x1}, {y1}, {x2}, {y2})"
            )

        cv2.imshow(window_name, draw_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def show_points(points: List[Tuple[int, int]], image, window_name: str = "points_result"):
        draw_image = image.copy()
        for point in points:
            cv2.circle(draw_image, point, 5, (0, 0, 255), -1)

        cv2.imshow(window_name, draw_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def find_way_stones(self, conf_threshold: float = 0.65) -> List[Tuple[int, int]]:
        map_image = self.dx.capture_fullscreen()
        if map_image is None:
            print("全屏截图失败")
            return []

        results = self.model.predict(
            source=map_image,
            conf=conf_threshold,
            save=False,
            verbose=False,
        )

        detect_result = results[0]
        boxes = detect_result.boxes
        # self.show_detect_boxes(detect_result, boxes, map_image)
        if boxes is None or len(boxes) == 0:
            print("未识别到传送锚点")
            return []

        center_points: List[Tuple[int, int]] = []

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            center_points.append((center_x, center_y))

        center_points.sort(key=lambda point: point[0], reverse=True)

        return center_points

    def is_target_way_stone(self, threshold: float = 0.80) -> bool:
        area_image = self.dx.capture_game_region(RIGHT_LOCATION_NAME_REGION)
        if area_image is None:
            print("截取右侧地名区域失败")
            return False

        area_gray = cv2.cvtColor(area_image, cv2.COLOR_BGR2GRAY)

        area_h, area_w = area_gray.shape[:2]
        template_h, template_w = self.area_template_gray.shape[:2]

        if template_h > area_h or template_w > area_w:
            print("模板尺寸大于搜索区域，无法匹配")
            return False

        result = cv2.matchTemplate(
            area_gray,
            self.area_template_gray,
            cv2.TM_CCOEFF_NORMED,
        )
        _, max_score, _, _ = cv2.minMaxLoc(result)

        print(f"模板匹配分数: {max_score:.4f}")
        return max_score >= threshold

    def detect_template(self, roi_points, template_name, threshold=0.6):
        """
        通用模板匹配方法，根据传入的模板名称进行匹配
        :param roi_points: 用于检测的区域
        :param template_name: 模板文件名（根据需求传入不同的模板）
        :param threshold: 模板匹配的阈值
        :return: 是否匹配成功，匹配位置
        """
        # 1. 加载模板 (灰度)
        template_path = f"../../assets/templates/{template_name}.png"  # 根据传入模板名称生成路径
        template_image = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

        if template_image is None:
            print(f"模板加载失败: {template_path}")
            return False, None

        h, w = template_image.shape[:2]  # 获取模板的高和宽，用于画框

        # 2. 截取 ROI 区域 (原图用于展示，search_image 用于匹配)
        original_roi_image = self.dx.capture_game_region(roi_points)
        if original_roi_image is None:
            return False, None

        # 3. 转换为灰度图进行匹配
        search_image = cv2.cvtColor(original_roi_image, cv2.COLOR_BGR2GRAY)

        # 4. 模板匹配
        result = cv2.matchTemplate(search_image, template_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # --- 画框展示逻辑开始 ---
        display_img = original_roi_image.copy()

        if max_val >= threshold:
            # 画矩形框
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(display_img, top_left, bottom_right, (0, 0, 255), 2)

            # 在框上方写上相似度
            cv2.putText(display_img, f"Match: {max_val:.2f}", (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # --- 画框展示逻辑结束 ---

        if max_val >= threshold:
            return True, max_loc
        return False, max_loc

    def can_press_f(self, image) -> bool:
        pass
if __name__ == "__main__":
    detector = GatherDetector()
    canf = detector.detect_f_prompt()
    print(canf)