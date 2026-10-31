"""計算曝光相關指標，輸出 CSV 並更新 README 表格。"""

import csv
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def measure(path: Path) -> dict[str, float]:
    with Image.open(path) as image:
        # Pillow 的 L 通道以 RGB 加權計算亮度，範圍為 0–255。
        pixels = np.asarray(ImageOps.exif_transpose(image).convert("L"), dtype=np.uint8)
    return {
        "mean": float(np.mean(pixels)),
        "std": float(np.std(pixels)),
        "dark": float(np.mean(pixels <= 5) * 100),
        "bright": float(np.mean(pixels >= 250) * 100),
    }


def main() -> None:
    source = ROOT / "original_image"
    after = ROOT / "after_image"
    records = []
    for path in sorted(source.iterdir()):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        result = after / path.name
        if not result.is_file():
            raise FileNotFoundError(f"找不到處理後圖片：{result}")
        records.append((path.name, measure(path), measure(result)))
    if not records:
        raise SystemExit("找不到原始圖片。")

    with (ROOT / "exposure_metrics.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["image", "version", "mean_brightness_0_255", "brightness_std_0_255", "dark_pixels_le_5_percent", "bright_pixels_ge_250_percent"])
        for name, original, processed in records:
            for version, metrics in (("original", original), ("processed", processed)):
                writer.writerow([name, version, *(f"{metrics[key]:.2f}" for key in ("mean", "std", "dark", "bright"))])

    start, end = "<!-- exposure-metrics-start -->", "<!-- exposure-metrics-end -->"
    lines = [start, "### 曝光指標（處理前 → 處理後）", "",
             "亮度依 RGB 加權轉成 0–255 的灰階值。平均亮度越高代表整體越亮；亮度標準差反映整體亮暗差異。暗部與亮部分別是亮度 ≤ 5 和 ≥ 250 的像素比例。", "",
             "| 圖片 | 平均亮度 | 亮度標準差 | 暗部比例 | 亮部比例 |", "| --- | --- | --- | --- | --- |"]
    for name, a, b in records:
        lines.append(f"| {name} | {a['mean']:.2f} → {b['mean']:.2f} | {a['std']:.2f} → {b['std']:.2f} | {a['dark']:.2f}% → {b['dark']:.2f}% | {a['bright']:.2f}% → {b['bright']:.2f}% |")
    lines += ["", "亮部與暗部比例是接近白色和黑色的像素比例，不能單獨證明細節已過曝或欠曝；指標也不能直接代表照片品質。完整數據見 `exposure_metrics.csv`。", "", "重新計算：`.\\.venv\\Scripts\\python.exe exposure_metrics.py`。", end]
    section = "\n".join(lines)
    readme = ROOT / "readme.md"
    content = readme.read_text(encoding="utf-8")
    if start in content and end in content:
        before, rest = content.split(start, 1)
        _, following = rest.split(end, 1)
        content = before + section + following
    else:
        content = content.rstrip() + "\n\n" + section + "\n"
    readme.write_text(content, encoding="utf-8")
    print(f"已計算 {len(records)} 張圖片，更新 exposure_metrics.csv 與 readme.md。")


if __name__ == "__main__":
    main()
