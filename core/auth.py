"""로그인·회원가입·로그아웃.

담당: 파트 A (인증·DB)
- 비밀번호 확인: Firebase Auth REST API (firebase-admin은 비밀번호 확인 기능이 없음)
- 토큰 검증: firebase_admin.auth.verify_id_token 으로 서버에서 다시 확인
- 역할: Firestore users/{uid}.role
"""

import requests
import streamlit as st
from firebase_admin import auth as admin_auth
from firebase_admin import firestore

from core.constants import DEFAULT_ROLE, ROLE_LABELS
from core.firebase import get_app, get_db, web_api_key

_BASE = "https://identitytoolkit.googleapis.com/v1/accounts"

# Firebase가 돌려주는 에러 코드를 한국어로 안내
_ERRORS = {
    "EMAIL_EXISTS": "이미 가입된 이메일입니다.",
    "EMAIL_NOT_FOUND": "가입되지 않은 이메일입니다.",
    "INVALID_PASSWORD": "비밀번호가 틀렸습니다.",
    "INVALID_LOGIN_CREDENTIALS": "이메일 또는 비밀번호가 틀렸습니다.",
    "WEAK_PASSWORD : Password should be at least 6 characters": "비밀번호는 6자 이상이어야 합니다.",
    "INVALID_EMAIL": "이메일 형식이 올바르지 않습니다.",
}


def _call(endpoint: str, email: str, password: str) -> dict:
    res = requests.post(
        f"{_BASE}:{endpoint}?key={web_api_key()}",
        json={"email": email, "password": password, "returnSecureToken": True},
        timeout=10,
    )
    data = res.json()
    if "error" in data:
        msg = data["error"].get("message", "")
        raise ValueError(_ERRORS.get(msg, f"인증 실패: {msg}"))
    return data


def _load_user(id_token: str, status=None) -> dict:
    say = status.write if status else (lambda *_: None)

    say("2/3 서버에서 토큰 검증 중...")
    get_app()
    decoded = admin_auth.verify_id_token(id_token)   # 서버에서 토큰 위조 여부 확인
    uid = decoded["uid"]

    say("3/3 Firestore에서 역할 정보 읽는 중...")
    try:
        doc = get_db().collection("users").document(uid).get(timeout=10)
    except Exception as e:
        raise RuntimeError(
            "Firestore 응답이 없습니다(10초 초과). Firestore Database 생성 여부, "
            "서비스 계정 키의 프로젝트, 네트워크(학교 와이파이)를 확인하세요."
        ) from e
    if not doc.exists:
        raise ValueError(f"역할 정보(users/{uid})가 없습니다. 관리자에게 문의하세요.")
    profile = doc.to_dict()
    return {
        "uid": uid,
        "email": decoded.get("email", ""),
        "name": profile.get("name", decoded.get("email", "")),
        "role": profile.get("role", DEFAULT_ROLE),
        "id_token": id_token,
    }


def sign_up(email: str, password: str, name: str) -> None:
    data = _call("signUp", email, password)
    get_db().collection("users").document(data["localId"]).set({
        "uid": data["localId"],
        "email": email,
        "name": name,
        "role": DEFAULT_ROLE,
        "created_at": firestore.SERVER_TIMESTAMP,
    })


def sign_in(email: str, password: str, status=None) -> dict:
    if status:
        status.write("1/3 Firebase에 비밀번호 확인 중...")
    data = _call("signInWithPassword", email, password)
    user = _load_user(data["idToken"], status)
    st.session_state["user"] = user
    return user


def sign_out() -> None:
    st.session_state.pop("user", None)


def current_user() -> dict | None:
    return st.session_state.get("user")


def login_page() -> None:
    """로그인하지 않은 사용자에게만 보이는 페이지."""
    st.title("교육용 웹 PACS")
    st.caption("공개 데이터와 모의 케이스로 작동하는 교육용 시스템입니다. 실제 진단에 사용할 수 없습니다.")

    tab_in, tab_up = st.tabs(["로그인", "회원가입"])
    with tab_in:
        with st.form("login"):
            email = st.text_input("이메일")
            pw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인", use_container_width=True):
                ok = False
                with st.status("로그인 중...", expanded=True) as status:
                    try:
                        sign_in(email.strip(), pw, status)
                        status.update(label="로그인 성공", state="complete")
                        ok = True
                    except ValueError as e:
                        status.update(label="로그인 실패", state="error")
                        st.error(str(e))
                    except Exception as e:
                        status.update(label="로그인 실패 (예상하지 못한 오류)", state="error")
                        st.exception(e)
                if ok:
                    st.rerun()
    with tab_up:
        with st.form("signup"):
            name = st.text_input("이름")
            email = st.text_input("이메일", key="su_email")
            pw = st.text_input("비밀번호 (6자 이상)", type="password", key="su_pw")
            if st.form_submit_button("회원가입", use_container_width=True):
                try:
                    sign_up(email, pw, name)
                    st.success(f"가입 완료. 기본 역할은 '{ROLE_LABELS[DEFAULT_ROLE]}'입니다. 로그인해 주세요.")
                except ValueError as e:
                    st.error(str(e))
