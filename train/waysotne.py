import random
import shutil
from pathlib import Path


def split_yolo_dataset(
    src_dir: str,
    out_dir: str,
    train_ratio: float = 0.8,
    image_exts: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".webp"),
    seed: int = 42,
    copy_json: bool = False,
):
    src_path = Path(src_dir)
    out_path = Path(out_dir)

    if not src_path.exists():
        raise FileNotFoundError(f"源目录不存在: {src_path}")

    classes_file = src_path / "classes.txt"
    if not classes_file.exists():
        raise FileNotFoundError(f"找不到 classes.txt: {classes_file}")

    pairs = []
    for img_path in src_path.iterdir():
        if not img_path.is_file():
            continue
        if img_path.suffix.lower() not in image_exts:
            continue

        txt_path = img_path.with_suffix(".txt")
        if txt_path.exists():
            pairs.append((img_path, txt_path))
        else:
            print(f"[跳过] 找不到同名 txt: {img_path.name}")

    if not pairs:
        raise RuntimeError("没有找到任何 图片 + 同名 txt 配对文件")

    random.seed(seed)
    random.shuffle(pairs)

    train_count = int(len(pairs) * train_ratio)
    train_pairs = pairs[:train_count]
    val_pairs = pairs[train_count:]

    (out_path / "images" / "train").mkdir(parents=True, exist_ok=True)
    (out_path / "images" / "val").mkdir(parents=True, exist_ok=True)
    (out_path / "labels" / "train").mkdir(parents=True, exist_ok=True)
    (out_path / "labels" / "val").mkdir(parents=True, exist_ok=True)

    if copy_json:
        (out_path / "json" / "train").mkdir(parents=True, exist_ok=True)
        (out_path / "json" / "val").mkdir(parents=True, exist_ok=True)

    shutil.copy2(classes_file, out_path / "classes.txt")

    def copy_pairs(pair_list, split_name: str):
        for img_path, txt_path in pair_list:
            shutil.copy2(img_path, out_path / "images" / split_name / img_path.name)
            shutil.copy2(txt_path, out_path / "labels" / split_name / txt_path.name)

            if copy_json:
                json_path = img_path.with_suffix(".json")
                if json_path.exists():
                    shutil.copy2(json_path, out_path / "json" / split_name / json_path.name)

    copy_pairs(train_pairs, "train")
    copy_pairs(val_pairs, "val")

    print("=" * 60)
    print(f"总样本数: {len(pairs)}")
    print(f"train: {len(train_pairs)}")
    print(f"val:   {len(val_pairs)}")
    print(f"输出目录: {out_path}")
    print("=" * 60)


def write_data_yaml(out_dir: str):
    out_path = Path(out_dir)
    classes_file = out_path / "classes.txt"

    if not classes_file.exists():
        raise FileNotFoundError(f"找不到 classes.txt: {classes_file}")

    class_names = [
        line.strip()
        for line in classes_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    yaml_lines = [
        f"path: {out_path.as_posix()}",
        "train: images/train",
        "val: images/val",
        "names:",
    ]

    for i, name in enumerate(class_names):
        yaml_lines.append(f"  {i}: {name}")

    data_yaml_path = out_path / "data.yaml"
    data_yaml_path.write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")

    print(f"已生成 data.yaml: {data_yaml_path}")


if __name__ == "__main__":
    output_dir = r"C:\Users\kazaf\Pictures\CESHI\dataset_yolo"

    split_yolo_dataset(
        src_dir=r"C:\Users\kazaf\Pictures\CESHI\aaa",
        out_dir=output_dir,
        train_ratio=0.8,
        seed=42,
        copy_json=False,
    )

    write_data_yaml(output_dir)