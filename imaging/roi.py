"""ROI(관심 영역) 분석.  담당: 파트 C"""

import numpy as np


def roi_stats(image: np.ndarray, x0: int, y0: int, x1: int, y1: int,
              pixel_spacing: list[float] | None = None) -> dict:
    """ROI 좌표는 [x0, x1) × [y0, y1). DICOM이면 Pixel Spacing으로 mm² 환산."""
    h, w = image.shape[:2]
    if not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
        raise ValueError(f"ROI가 영상 범위(가로 {w}, 세로 {h})를 벗어났거나 비어 있습니다.")
    region = image[y0:y1, x0:x1].astype(np.float64)
    result = {
        "roi": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
        "mean": float(region.mean()),
        "std": float(region.std()),
        "min": float(region.min()),
        "max": float(region.max()),
        "area_px": int(region.size),
        "area_mm2": None,
    }
    if pixel_spacing:
        row_mm, col_mm = pixel_spacing
        result["area_mm2"] = float(region.size * row_mm * col_mm)
    return result
