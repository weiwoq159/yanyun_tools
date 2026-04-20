from pathlib import Path

import torch
from ultralytics import YOLO


def main():
    project_root = Path(r"D:\work\mq\yanyun_tools")
    dataset_dir = project_root / "train" / "dataset_yolo"
    data_yaml = dataset_dir / "data.yaml"

    if not data_yaml.exists():
        raise FileNotFoundError(f"找不到 data.yaml: {data_yaml}")

    print("=" * 60)
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"Dataset yaml: {data_yaml}")
    print("Train device: cpu")
    print("=" * 60)

    model = YOLO("best.pt")

    model.train(
        data=str(data_yaml),
        imgsz=640,
        epochs=100,
        batch=8,
        device="cpu",
        workers=0,
        pretrained=True,
        project=str(project_root / "runs"),
        name="map_icon_train_cpu",
        exist_ok=True,
        optimizer="auto",
        verbose=True,
    )

    print("训练完成。")


if __name__ == "__main__":
    main()