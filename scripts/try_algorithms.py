"""알고리즘 4개를 한 영상에 적용해서 원본과 비교한 그림 한 장을 저장합니다.

실행 (프로젝트 폴더에서):
    uv run python scripts/try_algorithms.py                 # pydicom 예제 CT 사용
    uv run python scripts/try_algorithms.py 내영상.png       # 내가 가진 PNG/JPG/DICOM 사용
결과: data/output/compare.png
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
import numpy as np

from imaging.algorithms import bilateral, canny, clahe, otsu, to_uint8
from imaging.io import apply_window, load_image
from imaging.samples import sample_bytes

# 1) 영상 읽기
if len(sys.argv) > 1:
    path = Path(sys.argv[1])
    image, meta = load_image(path.name, path.read_bytes())
else:
    image, meta = load_image("ct.dcm", sample_bytes("CT (128×128, 척추 단면)"))

# 2) 알고리즘에 넣을 흑백 uint8 만들기 (CT면 헤더의 Window 값 사용)
if meta.get("window_center") is not None and meta.get("window_width"):
    gray = apply_window(image, meta["window_center"], meta["window_width"])
else:
    gray = to_uint8(image)

# 3) 알고리즘 적용 (원본 gray는 바뀌지 않음)
results = {
    "Original": gray,
    "CLAHE clip=2.0": clahe(gray, clip_limit=2.0, tile=8),
    "Bilateral d=9": bilateral(gray, d=9, sigma_color=75, sigma_space=75),
}
mask, th = otsu(gray)
results[f"Otsu th={th:.0f}"] = mask
results["Canny 50/150"] = canny(gray, 50, 150)

# 4) 작은 영상은 보기 좋게 키워서(최근접 보간) 2행 3열로 붙이기
scale = max(1, 256 // max(gray.shape))
tiles = []
for title, img in results.items():
    big = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    big = cv2.copyMakeBorder(big, 28, 4, 4, 4, cv2.BORDER_CONSTANT, value=0)
    cv2.putText(big, title, (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 1, cv2.LINE_AA)
    tiles.append(big)
tiles.append(np.zeros_like(tiles[0]))                      # 6칸 맞추기용 빈칸
grid = np.vstack([np.hstack(tiles[0:3]), np.hstack(tiles[3:6])])

out = Path("data/output")
out.mkdir(parents=True, exist_ok=True)
cv2.imwrite(str(out / "compare.png"), grid)
print(f"Otsu가 찾은 기준값: {th:.0f}")
print(f"저장: {(out / 'compare.png').resolve()}")
