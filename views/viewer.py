"""영상 뷰어: 원본 표시, 확대·축소, 이동, 밝기/대비 또는 Window/Level, 초기화.  담당: 파트 B

지금은 로컬 파일 업로드로만 동작하는 임시 버전입니다.
나중에 케이스 목록에서 고른 영상을 Storage에서 불러오도록 바꿉니다.
"""

import streamlit as st

from imaging.io import load_image

st.title("영상 뷰어")

file = st.file_uploader("영상 (PNG/JPG/DICOM)", type=["png", "jpg", "jpeg", "dcm"])
if file is None:
    st.info("영상을 올리면 여기에 표시됩니다.")
    st.stop()

try:
    image, meta = load_image(file.name, file.getvalue())
except ValueError as e:
    st.error(str(e))
    st.stop()

st.image(image, caption=f"원본 · {meta['format']} · {image.shape}", clamp=True)
st.json(meta, expanded=False)

# TODO(파트 B): 확대·축소, 이동(crop), 밝기/대비, DICOM Window/Level 프리셋, 초기화 버튼
