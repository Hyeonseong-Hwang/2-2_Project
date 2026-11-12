"""영상처리 알고리즘 3종 이상.  담당: 파트 C

규칙(안내문 4쪽)
- 서로 다른 목적의 알고리즘 3종 이상. 같은 알고리즘의 파라미터만 바꾼 것은 1종.
- 확대·축소·이동·밝기·Window/Level·파일 변환은 개수에 포함되지 않음.
- 모든 함수는 입력 배열을 바꾸지 않고 새 배열을 돌려줍니다.

추천 조합: 명암 조정(CLAHE) / 노이즈 제거(Median) / 경계 추출(Canny)
"""

import numpy as np

ALGORITHM_VERSION = "0.1.0"


def to_uint8(image: np.ndarray) -> np.ndarray:
    """DICOM(HU, float)도 처리할 수 있게 0~255로 정규화."""
    if image.dtype == np.uint8:
        return image.copy()
    lo, hi = float(image.min()), float(image.max())
    if hi == lo:
        return np.zeros_like(image, dtype=np.uint8)
    return ((image - lo) / (hi - lo) * 255).astype(np.uint8)


# TODO(파트 C): def clahe(image, clip_limit=2.0, tile=8) -> np.ndarray
# TODO(파트 C): def median_filter(image, ksize=5) -> np.ndarray
# TODO(파트 C): def canny(image, low=50, high=150) -> np.ndarray
