"""케이스 목록: 검색·필터, 처리할 업무와 완료된 업무 구분.  담당: 파트 A·B"""

import streamlit as st

from core.auth import current_user
from core.constants import ROLE_REVIEWER, STATUS_DONE, STATUS_LABELS
from core.db import list_cases

user = current_user()
st.title("케이스 목록")

col1, col2 = st.columns(2)
status = col1.selectbox("상태", ["전체", *STATUS_LABELS.keys()],
                        format_func=lambda s: "전체" if s == "전체" else STATUS_LABELS[s])
mine = col2.checkbox("내 담당만 보기", value=user["role"] == ROLE_REVIEWER)

cases = list_cases(
    status=None if status == "전체" else status,
    assignee_uid=user["uid"] if mine else None,
)

todo = [c for c in cases if c["status"] != STATUS_DONE]
done = [c for c in cases if c["status"] == STATUS_DONE]

tab_todo, tab_done = st.tabs([f"처리할 업무 ({len(todo)})", f"완료 ({len(done)})"])
for tab, rows in ((tab_todo, todo), (tab_done, done)):
    with tab:
        if not rows:
            st.info("해당하는 케이스가 없습니다.")
        for c in rows:
            st.write(f"**{c['case_id']}** · {c['modality']} · {c['body_part']} · "
                     f"{c['study_date']} · {STATUS_LABELS[c['status']]}")

# TODO(파트 B): 케이스를 고르면 st.session_state["case_id"]에 넣고 뷰어 페이지로 이동
# TODO(파트 A): 날짜·모달리티 필터 추가
