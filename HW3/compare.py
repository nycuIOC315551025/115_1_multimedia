"""將原圖與處理後的圖片並排，產生左右對照圖。"""

from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
source = ROOT / "original_image"
processed = ROOT / "after_image"
destination = ROOT / "left_and_right_compare"
destination.mkdir(exist_ok=True)

files = [path for path in sorted(source.iterdir()) if path.is_file() and (processed / path.name).is_file()]
# 固定亂數種子，讓重跑程式後圖像順序與 README 的答案一致。
processed_left = [True] * (len(files) // 2) + [False] * (len(files) - len(files) // 2)
random.Random(42).shuffle(processed_left)
rows = []
for path, is_left in zip(files, processed_left):
    other = processed / path.name
    if not path.is_file() or not other.is_file():
        continue
    with Image.open(path) as original, Image.open(other) as result:
        original = ImageOps.exif_transpose(original).convert("RGB")
        result = ImageOps.exif_transpose(result).convert("RGB")
        width = max(original.width, result.width)
        height = max(original.height, result.height)
        gap = max(8, width // 100)
        left, right = (result, original) if is_left else (original, result)
        header = max(36, width // 12)
        canvas = Image.new("RGB", (2 * width + gap, height + header), (245, 245, 245))
        canvas.paste(left, ((width - left.width) // 2, header))
        canvas.paste(right, (width + gap + (width - right.width) // 2, header))
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("arial.ttf", max(18, header * 2 // 3))
        except OSError:
            font = ImageFont.load_default()
        draw.text((width // 2, header // 2), "A", font=font, fill=(30, 30, 30), anchor="mm")
        draw.text((width + gap + width // 2, header // 2), "B", font=font, fill=(30, 30, 30), anchor="mm")
        output = destination / f"{path.stem}_compare.png"
        canvas.save(output)
        rows.append(f"| {output.name} | {'A（左）' if is_left else 'B（右）'} |")
        print(output.name)

start, end = "<!-- compare-answers-start -->", "<!-- compare-answers-end -->"
answers = "\n".join([start, "### 左右對照圖答案", "", "A 是左圖，B 是右圖。", "", "| 對照圖 | 處理後的圖片 |", "| --- | --- |", *rows, end])
readme = ROOT / "readme.md"
content = readme.read_text(encoding="utf-8")
if start in content and end in content:
    before, rest = content.split(start, 1)
    _, after = rest.split(end, 1)
    content = before + answers + after
else:
    content = content.rstrip() + "\n\n" + answers + "\n"
readme.write_text(content, encoding="utf-8")
