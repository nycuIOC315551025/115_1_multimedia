"""使用自動 Gamma 校正與 CLAHE 批次調整照片。"""

import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parent
EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def clahe(luminance: np.ndarray, tiles: int = 8, clip_limit: float = 1.4) -> np.ndarray:
    """限制對比度自適應直方圖均衡化，並在相鄰區塊間雙線性插值。"""
    height, width = luminance.shape
    rows, cols = min(tiles, height), min(tiles, width)
    y_edges = np.linspace(0, height, rows + 1, dtype=int)
    x_edges = np.linspace(0, width, cols + 1, dtype=int)
    tables = np.empty((rows, cols, 256), dtype=np.float64)
    for row in range(rows):
        for col in range(cols):
            tile = luminance[y_edges[row]:y_edges[row + 1], x_edges[col]:x_edges[col + 1]]
            hist = np.bincount(tile.ravel(), minlength=256)
            limit = max(1, int(clip_limit * tile.size / 256))
            excess = int(np.maximum(hist - limit, 0).sum())
            hist = np.minimum(hist, limit)
            hist += excess // 256
            hist[:excess % 256] += 1
            tables[row, col] = np.cumsum(hist) * (255.0 / tile.size)

    # 依各區塊中心定位，以插值消除區塊邊界。
    y_centers = (y_edges[:-1] + y_edges[1:] - 1) / 2
    x_centers = (x_edges[:-1] + x_edges[1:] - 1) / 2
    yy = np.interp(np.arange(height), y_centers, np.arange(rows))
    xx = np.interp(np.arange(width), x_centers, np.arange(cols))
    y0 = np.floor(yy).astype(int)[:, None]
    x0 = np.floor(xx).astype(int)[None, :]
    y1 = np.minimum(y0 + 1, rows - 1)
    x1 = np.minimum(x0 + 1, cols - 1)
    wy = (yy[:, None] - y0)
    wx = (xx[None, :] - x0)
    top = tables[y0, x0, luminance] * (1 - wx) + tables[y0, x1, luminance] * wx
    bottom = tables[y1, x0, luminance] * (1 - wx) + tables[y1, x1, luminance] * wx
    return top * (1 - wy) + bottom * wy


def correct_exposure(image: Image.Image, target: float) -> tuple[Image.Image, float]:
    """先以 Gamma 微調整體曝光，再用 CLAHE 增加局部亮度對比。"""
    image = ImageOps.exif_transpose(image).convert("RGB")
    sample = image.copy()
    sample.thumbnail((512, 512))
    histogram = sample.convert("L").histogram()
    pixel_count = sum(histogram)
    mean = sum(value * count for value, count in enumerate(histogram)) / pixel_count / 255
    # 全黑及全白沒有可供調整的細節，也避免 log(0) 或除以零。
    if mean <= 0.001 or mean >= 0.999:
        return image, 1.0
    # 減弱自動校正，保留夕陽、陰天等場景原本的氣氛。
    estimated_gamma = math.log(target) / math.log(mean)
    gamma = max(0.75, min(1.04, 1 + (estimated_gamma - 1) * 0.7))
    ycbcr = np.array(image.convert("YCbCr"))
    luminance = ycbcr[:, :, 0]
    lookup = np.array([round(255 * (value / 255) ** gamma) for value in range(256)], dtype=np.uint8)
    corrected = lookup[luminance]
    enhanced = clahe(corrected)
    # 混合原亮度與 CLAHE 結果，避免局部對比和雜訊過強。
    ycbcr[:, :, 0] = np.clip(0.7 * corrected + 0.3 * enhanced, 0, 255).astype(np.uint8)
    return Image.fromarray(ycbcr, "YCbCr").convert("RGB"), gamma


def main() -> None:
    parser = argparse.ArgumentParser(description="用自動 Gamma 校正與 CLAHE 調整圖片曝光")
    parser.add_argument("--target", type=float, default=0.5, help="目標平均亮度，介於 0 和 1 之間（預設 0.5）")
    args = parser.parse_args()
    if not 0 < args.target < 1:
        parser.error("--target 必須介於 0 和 1 之間，不含 0 和 1")
    source = ROOT / "original_image"
    destination = ROOT / "after_image"
    if not source.is_dir():
        parser.error(f"找不到輸入資料夾：{source}")
    destination.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in source.iterdir() if path.is_file() and path.suffix.lower() in EXTENSIONS)
    if not files:
        print(f"沒有找到圖片：{source}")
        return
    failures = 0
    for path in files:
        try:
            with Image.open(path) as image:
                result, gamma = correct_exposure(image, args.target)
                result.save(destination / path.name)
            print(f"{path.name} -> after_image/{path.name} (gamma={gamma:.2f})")
        except (OSError, ValueError, UnidentifiedImageError) as error:
            failures += 1
            print(f"處理失敗：{path.name}：{error}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
