"""앱 시작점. 실행: uv run streamlit run app.py

로그인 여부와 역할에 따라 보이는 페이지를 나눕니다.
화면에서 메뉴를 숨기는 것과 별개로, 실제 권한 검사는 core/db.py 쓰기 함수에서 다시 합니다.
"""

import streamlit as st

from core.auth import current_user, login_page, sign_out
from core.constants import ROLE_ADMIN, ROLE_LABELS, ROLE_REGISTRAR

st.set_page_config(page_title="교육용 웹 PACS", page_icon="🩻", layout="wide")

user = current_user()

if user is None:
    st.navigation([st.Page(login_page, title="로그인")]).run()
    st.stop()

with st.sidebar:
    st.write(f"**{user['name']}**")
    st.caption(ROLE_LABELS.get(user["role"], user["role"]))
    if st.button("로그아웃", use_container_width=True):
        sign_out()
        st.rerun()

pages = {
    "업무": [
        st.Page("views/cases.py", title="케이스 목록", default=True),     # 파트 A·B
        st.Page("views/viewer.py", title="영상 뷰어"),                    # 파트 B
        st.Page("views/processing.py", title="영상처리·ROI"),             # 파트 C
        st.Page("views/feature.py", title="특화 기능"),                   # 파트 D
    ],
}
if user["role"] in (ROLE_REGISTRAR, ROLE_ADMIN):
    pages["업무"].insert(1, st.Page("views/register.py", title="케이스 등록"))   # 파트 A·B
if user["role"] == ROLE_ADMIN:
    pages["관리"] = [st.Page("views/admin.py", title="배정·진행 현황")]          # 파트 A·D

st.navigation(pages).run()
