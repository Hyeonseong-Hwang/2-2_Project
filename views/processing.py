"""영상처리 + ROI 분석 화면.  담당: 파트 C

흐름: 영상 고르기 → 흑백 uint8 변환 → 알고리즘·파라미터 선택 → 원본/결과 비교 → ROI 통계
TODO(파트 A·C): 실행 결과를 processing_runs 컬렉션에 저장 (알고리즘, 버전, 파라미터, ROI, 특징값)
TODO(파트 B·C): 업로드 대신 케이스 목록에서 고른 영상을 Storage에서 불러오기
"""

import cv2
import numpy as np
import streamlit as st

from imaging import algorithms as alg
from imaging.io import WINDOW_PRESETS, apply_window, load_image
from imaging.roi import roi_stats
from imaging.samples import SAMPLES, sample_bytes

st.title("영상처리·ROI")
st.caption("교육용 결과입니다. 처리 결과의 픽셀 값은 원본 측정값(HU)과 다를 수 있습니다.")

# ── 1. 영상 고르기 ─────────────────────────────────────────
source = st.radio("영상 선택", ["pydicom 예제", "파일 업로드"], horizontal=True)
if source == "pydicom 예제":
    label = st.selectbox("예제 영상", list(SAMPLES))
    filename, data = f"{SAMPLES[label]}.dcm", sample_bytes(label)
else:
    file = st.file_uploader("PNG / JPG / DICOM", type=["png", "jpg", "jpeg", "dcm"])
    if file is None:
        st.info("영상을 올려주세요.")
        st.stop()
    filename, data = file.name, file.getvalue()

try:
    image, meta = load_image(filename, data)
except ValueError as e:
    st.error(str(e))
    st.stop()

# ── 2. 알고리즘 입력용 흑백 uint8 만들기 ───────────────────
if meta["format"] == "DICOM" and image.ndim == 2:
    presets = ["헤더 값"] * (meta.get("window_center") is not None) + ["최소~최대"] + list(WINDOW_PRESETS)
    win = st.selectbox("표시 범위 (Window/Level)", presets,
                       help="DICOM은 0~255보다 넓은 값을 가져서, 어떤 범위를 0~255에 맞출지 먼저 정합니다.")
    if win == "헤더 값":
        gray = apply_window(image, meta["window_center"], meta["window_width"])
    elif win == "최소~최대":
        gray = alg.to_uint8(image)
    else:
        gray = apply_window(image, *WINDOW_PRESETS[win])
else:
    gray = alg.to_uint8(image)

# ── 3. 알고리즘·파라미터 ───────────────────────────────────
choice = st.selectbox("알고리즘", list(alg.ALGORITHMS))
key = alg.ALGORITHMS[choice]
params, info = {}, ""

c1, c2, c3 = st.columns(3)
if key == "clahe":
    params["clip_limit"] = c1.slider("clip_limit (대비 상한)", 0.5, 8.0, 2.0, 0.5)
    params["tile"] = c2.slider("tile (칸 개수)", 2, 16, 8)
    result = alg.clahe(gray, **params)
elif key == "bilateral":
    params["d"] = c1.slider("d (주변 범위)", 3, 15, 9, 2)
    params["sigma_color"] = c2.slider("sigma_color (밝기 허용 차이)", 10, 200, 75, 5)
    params["sigma_space"] = c3.slider("sigma_space (거리 허용)", 10, 200, 75, 5)
    result = alg.bilateral(gray, **params)
elif key == "otsu":
    result, th = alg.otsu(gray)
    params["threshold"] = th
    info = f"Otsu가 자동으로 찾은 기준값: **{th:.0f}** (이 값보다 밝으면 흰색)"
else:
    params["low"] = c1.slider("low", 0, 254, 50)
    params["high"] = c2.slider("high", params["low"] + 1, 255, max(150, params["low"] + 1))
    result = alg.canny(gray, **params)

# ── 4. 원본 / 결과 비교 ────────────────────────────────────
if info:
    st.markdown(info)
zoom = st.slider("표시 배율", 1, 8, max(1, 384 // max(gray.shape)),
                 help="작은 영상을 키워서 봅니다. 화면 표시만 바뀌고 계산에는 영향이 없습니다.")


def show(img):
    return cv2.resize(img, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_NEAREST)


left, right = st.columns(2)
left.image(show(gray), caption=f"입력 ({meta['format']}, {gray.shape[1]}×{gray.shape[0]})")
right.image(show(result), caption=f"결과: {choice}")

ok, png = cv2.imencode(".png", result)
st.download_button("결과 PNG 저장", png.tobytes(), file_name=f"{key}_result.png", mime="image/png")

# ── 5. ROI 분석 ────────────────────────────────────────────
st.subheader("ROI 분석")
h, w = gray.shape
r1, r2 = st.columns(2)
x0, x1 = r1.slider("가로 범위 (x)", 0, w, (w // 4, w * 3 // 4))
y0, y1 = r2.slider("세로 범위 (y)", 0, h, (h // 4, h * 3 // 4))

target = st.radio("측정 대상", ["원본 값 (DICOM이면 HU)", "처리 결과"], horizontal=True)
measure_on = image if (target.startswith("원본") and image.ndim == 2) else (gray if target.startswith("원본") else result)

try:
    stats = roi_stats(measure_on, x0, y0, x1, y1, meta.get("pixel_spacing"))
except ValueError as e:
    st.error(str(e))
    st.stop()

boxed = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
cv2.rectangle(boxed, (x0, y0), (max(x0, x1 - 1), max(y0, y1 - 1)), (255, 80, 80), 1)
st.image(show(boxed), caption="ROI 위치 (빨간 사각형)")

m = st.columns(4)
m[0].metric("평균", f"{stats['mean']:.1f}")
m[1].metric("표준편차", f"{stats['std']:.1f}")
m[2].metric("면적 (픽셀)", f"{stats['area_px']:,}")
m[3].metric("면적 (mm²)", f"{stats['area_mm2']:.1f}" if stats["area_mm2"] else "간격 정보 없음")
if not meta.get("pixel_spacing"):
    st.caption("PNG/JPG는 픽셀 간격 정보가 없어 면적을 픽셀 단위로만 표시합니다.")

with st.expander("이번 실행 기록 (processing_runs에 저장할 내용)"):
    st.json({"algorithm": key, "version": alg.ALGORITHM_VERSION, "params": params,
             "roi": stats["roi"], "features": {k: stats[k] for k in ("mean", "std", "area_px", "area_mm2")},
             "measured_on": target, "source": filename})
