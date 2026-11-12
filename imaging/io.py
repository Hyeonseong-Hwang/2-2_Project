"""영상 파일 읽기: PNG/JPG/DICOM을 NumPy 배열 + 메타데이터로 바꿉니다.  담당: 파트 B

- 원본 배열은 절대 수정하지 않습니다. 처리할 때는 항상 .copy() 해서 씁니다.
- DICOM은 저장값을 HU로 바꾼 float32 배열을 돌려줍니다(화면 표시는 Window/Level 후).
"""

from io import BytesIO

import cv2
import numpy as np
import pydicom
from pydicom.errors import InvalidDicomError


def load_image(filename: str, data: bytes) -> tuple[np.ndarray, dict]:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "dcm":
        return _load_dicom(data)
    if ext in ("png", "jpg", "jpeg"):
        return _load_raster(data, ext)
    raise ValueError(f"지원하지 않는 형식입니다: .{ext} (PNG, JPG, DICOM만 가능)")


def _load_raster(data: bytes, ext: str) -> tuple[np.ndarray, dict]:
    arr = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("이미지 파일을 읽지 못했습니다. 파일이 손상되었거나 확장자와 내용이 다릅니다.")
    h, w = image.shape
    return image, {"format": ext.upper(), "rows": h, "cols": w, "pixel_spacing": None}


def _load_dicom(data: bytes) -> tuple[np.ndarray, dict]:
    try:
        ds = pydicom.dcmread(BytesIO(data))
        raw = ds.pixel_array.astype(np.float32)
    except (InvalidDicomError, AttributeError, ValueError) as e:
        raise ValueError(f"DICOM 파일을 읽지 못했습니다: {e}") from e
    slope = float(getattr(ds, "RescaleSlope", 1) or 1)
    intercept = float(getattr(ds, "RescaleIntercept", 0) or 0)
    hu = raw * slope + intercept
    spacing = getattr(ds, "PixelSpacing", None)
    meta = {
        "format": "DICOM",
        "rows": int(ds.Rows),
        "cols": int(ds.Columns),
        "modality": str(getattr(ds, "Modality", "")),
        "study_date": str(getattr(ds, "StudyDate", "")),
        "body_part": str(getattr(ds, "BodyPartExamined", "")),
        "sop_uid": str(getattr(ds, "SOPInstanceUID", "")),
        "pixel_spacing": [float(v) for v in spacing] if spacing else None,
        "window_center": _first(getattr(ds, "WindowCenter", None)),
        "window_width": _first(getattr(ds, "WindowWidth", None)),
    }
    return hu, meta


def _first(v):
    if v is None:
        return None
    try:
        return float(v[0])
    except (TypeError, IndexError):
        return float(v)


def apply_window(hu: np.ndarray, level: float, width: float) -> np.ndarray:
    """Window/Level 적용 → 0~255 uint8 (화면 표시용)."""
    if width <= 0:
        raise ValueError("Window Width는 0보다 커야 합니다.")
    lo, hi = level - width / 2, level + width / 2
    out = (np.clip(hu, lo, hi) - lo) / (hi - lo) * 255
    return out.astype(np.uint8)


WINDOW_PRESETS = {  # (Level, Width) — 특강 자료 기준
    "폐": (-600, 1500),
    "연부조직": (40, 400),
    "뼈": (400, 1800),
    "뇌": (40, 80),
}
