"""pydicom 예제 영상을 data/samples/ 에 .dcm 파일과 .png 미리보기로 꺼내 저장합니다.

실행 (프로젝트 폴더에서): uv run python scripts/export_samples.py
결과: data/samples/ct.dcm, data/samples/ct.png ... (Finder에서 PNG를 바로 열어볼 수 있음)
data/ 폴더는 .gitignore 에 들어 있어서 Git에 올라가지 않습니다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # 프로젝트 루트를 import 경로에 추가

import cv2

from imaging.algorithms import to_uint8
from imaging.io import apply_window, load_image
from imaging.samples import SAMPLES, sample_bytes

out_dir = Path("data/samples")
out_dir.mkdir(parents=True, exist_ok=True)

for label, name in SAMPLES.items():
    data = sample_bytes(label)
    (out_dir / f"{name}.dcm").write_bytes(data)

    image, meta = load_image(f"{name}.dcm", data)
    # CT처럼 헤더에 Window 값이 있으면 그 값으로, 없으면 최솟값~최댓값으로 보기 좋게 변환
    if meta.get("window_center") is not None and meta.get("window_width"):
        preview = apply_window(image, meta["window_center"], meta["window_width"])
    else:
        preview = to_uint8(image)
    cv2.imwrite(str(out_dir / f"{name}.png"), preview)

    print(f"{label:<22} → {name}.dcm / {name}.png  "
          f"모달리티={meta.get('modality')}  크기={meta['rows']}×{meta['cols']}  "
          f"픽셀간격={meta.get('pixel_spacing')}")

print(f"\n저장 위치: {out_dir.resolve()}")
