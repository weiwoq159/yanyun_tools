# from ultralytics import YOLO
#
# model = YOLO(r"D:\work\mq\yanyun_tools\train\best.pt")
# metrics = model.val(data=r"D:\work\mq\yanyun_tools\train\dataset_yolo\data.yaml", imgsz=640)
#
# print("mAP50-95:", metrics.box.map)
# print("mAP50:", metrics.box.map50)
# print("mAP75:", metrics.box.map75)

from pathlib import Path

import cv2
from ultralytics import YOLO
from capture.dxcam_capture import DXCamCapture

dx = DXCamCapture()
# ===== 1. 配置区 =====
MODEL_PATH = r"D:\work\mq\yanyun_tools\train\best.pt"
IMAGE_PATH = r"D:\work\mq\yanyun_tools\debug\test.png"

CONF_THRESHOLD = 0.25
WINDOW_NAME = "YOLO Detect Result"


def main():
    model_path = Path(MODEL_PATH)

    if not model_path.exists():
        raise FileNotFoundError(f"模型文件不存在: {model_path}")

    # ===== 2. 加载模型 =====
    model = YOLO(str(model_path))

    # ===== 3. 读取图片 =====
    image = dx.capture_fullscreen()

    # ===== 4. 推理 =====
    results = model.predict(
        source=image,
        conf=CONF_THRESHOLD,
        save=False,
        verbose=False,
    )

    # Ultralytics 对单张图返回一个 results[0]
    result = results[0]

    # ===== 5. 手动画框 =====
    boxes = result.boxes




if __name__ == "__main__":
    main()