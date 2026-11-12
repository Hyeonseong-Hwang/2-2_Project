"""관리자: 검토 담당자 배정, 진행 현황.  담당: 파트 A·D"""

import streamlit as st

from core.auth import current_user
from core.constants import ROLE_REVIEWER, STATUS_ASSIGNED, STATUS_LABELS, STATUS_RECEIVED
from core.db import change_status, list_cases, list_users
from core.rules import PermissionDenied

user = current_user()
st.title("배정·진행 현황")

all_cases = list_cases()
cols = st.columns(len(STATUS_LABELS))
for col, (key, label) in zip(cols, STATUS_LABELS.items()):
    col.metric(label, sum(1 for c in all_cases if c["status"] == key))

st.subheader("접수된 케이스 배정")
received = [c for c in all_cases if c["status"] == STATUS_RECEIVED]
reviewers = list_users(ROLE_REVIEWER)

if not received:
    st.info("배정할 케이스가 없습니다.")
elif not reviewers:
    st.warning("검토 담당자 계정이 없습니다.")
else:
    case_id = st.selectbox("케이스", [c["case_id"] for c in received])
    reviewer = st.selectbox("검토 담당자", reviewers, format_func=lambda u: u.get("name", u["uid"]))
    if st.button("배정"):
        try:
            change_status(user, case_id, STATUS_ASSIGNED, assignee_uid=reviewer["uid"])
            st.success(f"{case_id} → {reviewer.get('name')} 배정 완료")
            st.rerun()
        except (PermissionDenied, ValueError) as e:
            st.error(str(e))
