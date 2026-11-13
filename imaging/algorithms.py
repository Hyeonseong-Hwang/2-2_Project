"""영상처리 알고리즘 3종 이상.  담당: 파트 C

규칙(안내문 4쪽)
- 서로 다른 목적의 알고리즘 3종 이상. 같은 알고리즘의 파라미터만 바꾼 것은 1종.
- 확대·축소·이동·밝기·Window/Level·파일 변환은 개수에 포함되지 않음.
- 모든 함수는 입력 배열을 바꾸지 않고 새 배열을 돌려줍니다.

| 목적        | 알고리즘          | 함수          |
| 명암 조정   | CLAHE             | clahe         |
| 노이즈 제거 | Bilateral 필터    | bilateral     |
| 영역 추출   | Otsu 이진화       | otsu          |
| 경계 추출   | Canny 에지 검출   | canny         |
"""

import cv2
import numpy as np

ALGORITHM_VERSION = "0.2.0"


def to_uint8(image: np.ndarray) -> np.ndarray:
    """어떤 영상이든 알고리즘에 넣을 수 있는 흑백 uint8(0~255)로 바꿉니다.

    - 컬러(H, W, 3) → 흑백
    - DICOM(HU, float/int16 등) → 최솟값~최댓값을 0~255로 늘림
    CT를 원하는 조직 기준으로 보고 싶으면 이 함수 대신 imaging.io.apply_window 결과를 넣습니다.
    """
    img = image
    if img.ndim == 3:
        img = cv2.cvtColor(to_uint8_plain(img), cv2.COLOR_RGB2GRAY)
    return to_uint8_plain(img)


def to_uint8_plain(img: np.ndarray) -> np.ndarray:
    if img.dtype == np.uint8:
        return img.copy()
    lo, hi = float(img.min()), float(img.max())
    if hi == lo:
        return np.zeros(img.shape, dtype=np.uint8)
    return ((img.astype(np.float32) - lo) / (hi - lo) * 255).astype(np.uint8)


def _check(gray: np.ndarray) -> None:
    if gray.ndim != 2 or gray.dtype != np.uint8:
        raise ValueError("흑백 uint8 영상만 처리할 수 있습니다. 먼저 to_uint8()을 거치세요.")


# ── ① 명암 조정: CLAHE ─────────────────────────────────────
def clahe(gray: np.ndarray, clip_limit: float = 2.0, tile: int = 8) -> np.ndarray:
    """영상을 tile×tile 칸으로 나눠 칸마다 대비를 키우되, clip_limit로 과한 증폭을 막습니다."""
    _check(gray)
    if clip_limit <= 0 or tile < 1:
        raise ValueError("clip_limit는 0보다 크고, tile은 1 이상이어야 합니다.")
    return cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile, tile)).apply(gray)


# ── ② 노이즈 제거: Bilateral 필터 ──────────────────────────
def bilateral(gray: np.ndarray, d: int = 9, sigma_color: float = 75, sigma_space: float = 75) -> np.ndarray:
    """가깝고 밝기가 비슷한 픽셀끼리만 평균 → 노이즈는 줄고 경계는 유지됩니다."""
    _check(gray)
    if d < 1:
        raise ValueError("d는 1 이상이어야 합니다.")
    return cv2.bilateralFilter(gray, d, sigma_color, sigma_space)


def gaussian(gray: np.ndarray, ksize: int = 9) -> np.ndarray:
    """Bilateral과 비교하기 위한 기준(경계까지 흐려짐). 알고리즘 개수에는 넣지 않습니다."""
    _check(gray)
    k = ksize if ksize % 2 == 1 else ksize + 1
    return cv2.GaussianBlur(gray, (k, k), 0)


# ── ③ 영역 추출: Otsu 이진화 ───────────────────────────────
def otsu(gray: np.ndarray) -> tuple[np.ndarray, float]:
    """두 그룹이 가장 잘 갈리는 기준값을 자동으로 찾아 흰색(255)/검은색(0) 마스크를 만듭니다.
    반환: (마스크, Otsu가 찾은 기준값)"""
    _check(gray)
    threshold, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return mask, float(threshold)


# ── ④ 경계 추출: Canny ─────────────────────────────────────
def canny(gray: np.ndarray, low: int = 50, high: int = 150) -> np.ndarray:
    """기울기가 high 이상이면 경계, low 미만이면 버림, 그 사이는 경계와 이어질 때만 남깁니다."""
    _check(gray)
    if not 0 <= low < high:
        raise ValueError("0 ≤ low < high 이어야 합니다.")
    return cv2.Canny(gray, low, high)


# 화면(views/processing.py)에서 쓰는 목록
ALGORITHMS = {
    "CLAHE (명암 조정)": "clahe",
    "Bilateral 필터 (노이즈 제거)": "bilateral",
    "Otsu 이진화 (영역 추출)": "otsu",
    "Canny 에지 검출 (경계 추출)": "canny",
}
