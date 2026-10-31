
### 為什麼選這些
019 <-- 陰天
32 <-- 過鋪
13 <-- 夕陽
87 <-- 一般白天
90 <-- 神奇視角


### 要幹嘛
- 用經典演算法調整曝光，過曝之類的

### 執行方式

```powershell
.\.venv\Scripts\python.exe test.py
```

程式先根據平均亮度自動選擇 Gamma 值，再對亮度通道套用 CLAHE（限制對比度自適應直方圖均衡化），改善局部對比。結果與原亮度混合，減少過度處理；輸出存入 `after_image`。可用 `--target 0.6` 改變目標亮度（預設為 0.5）。完全過曝成純白的細節無法還原。

目前的 `.venv` 使用本機既有 Python 環境中的 Pillow 和 NumPy；若要在其他電腦建立環境，可以執行 `python -m venv .venv`，再執行 `.\.venv\Scripts\python.exe -m pip install Pillow numpy`。

<!-- compare-answers-start -->
### 左右對照圖答案

A 是左圖，B 是右圖。

| 對照圖 | 處理後的圖片 |
| --- | --- |
| img_013_SRF_4_HR_compare.png | B（右） |
| img_019_SRF_4_HR_compare.png | A（左） |
| img_032_SRF_4_HR_compare.png | B（右） |
| img_087_SRF_4_HR_compare.png | B（右） |
| img_090_SRF_4_HR_compare.png | A（左） |
<!-- compare-answers-end -->

<!-- exposure-metrics-start -->
### 曝光指標（處理前 → 處理後）

亮度依 RGB 加權轉成 0–255 的灰階值。平均亮度越高代表整體越亮；亮度標準差反映整體亮暗差異。暗部與亮部分別是亮度 ≤ 5 和 ≥ 250 的像素比例。

| 圖片 | 平均亮度 | 亮度標準差 | 暗部比例 | 亮部比例 |
| --- | --- | --- | --- | --- |
| img_013_SRF_4_HR.png | 112.75 → 122.99 | 56.91 → 58.35 | 0.79% → 0.67% | 0.00% → 0.00% |
| img_019_SRF_4_HR.png | 102.51 → 111.95 | 75.21 → 75.25 | 13.31% → 10.37% | 0.94% → 0.87% |
| img_032_SRF_4_HR.png | 141.97 → 138.54 | 81.02 → 78.82 | 1.31% → 1.58% | 7.93% → 6.43% |
| img_087_SRF_4_HR.png | 115.41 → 121.38 | 66.52 → 64.55 | 2.28% → 1.87% | 0.48% → 0.44% |
| img_090_SRF_4_HR.png | 67.34 → 89.71 | 56.29 → 54.20 | 0.48% → 0.02% | 2.97% → 2.96% |

亮部與暗部比例是接近白色和黑色的像素比例，不能單獨證明細節已過曝或欠曝；指標也不能直接代表照片品質。完整數據見 `exposure_metrics.csv`。

重新計算：`.\.venv\Scripts\python.exe exposure_metrics.py`。
<!-- exposure-metrics-end -->
