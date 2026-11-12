"""케이스 등록 (등록 담당자·관리자 전용).  담당: 파트 A·B"""

import streamlit as st

from core.auth import current_user
from core.db import create_case
from core.rules import PermissionDenied

user = current_user()
st.title("케이스 등록")
st.caption("실제 환자 정보는 입력하지 않습니다. 모의 ID를 사용합니다.")

with st.form("new_case"):
    case_id = st.text_input("케이스 ID (예: CASE-0001)")
    patient_id = st.text_input("모의 환자 ID (예: MOCK-P001)")
    study_date = st.date_input("검사일")
    modality = st.selectbox("모달리티", ["CT", "MR", "CR/DX (X-ray)", "US", "PT", "기타"])
    body_part = st.text_input("촬영 부위 (예: CHEST)")
    if st.form_submit_button("등록"):
        if not case_id or not patient_id:
            st.error("케이스 ID와 모의 환자 ID는 필수입니다.")
        else:
            try:
                create_case(user, case_id.strip(), patient_id.strip(),
                            study_date.isoformat(), modality, body_part.strip())
                st.success(f"{case_id} 등록 완료 (상태: 접수)")
            except (PermissionDenied, ValueError) as e:
                st.error(str(e))

# TODO(파트 B): 영상 파일 업로드 → 형식 검사 → Storage 저장 → images 컬렉션 기록
