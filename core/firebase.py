"""Firebase 초기화. 앱 전체에서 한 번만 연결하고 재사용합니다.

담당: 파트 A (인증·DB)
비밀키는 .streamlit/secrets.toml 에만 넣고, 절대 Git에 올리지 않습니다.
"""

import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore, storage


@st.cache_resource
def get_app():
    if firebase_admin._apps:
        return firebase_admin.get_app()
    cred = credentials.Certificate(dict(st.secrets["firebase_service_account"]))
    return firebase_admin.initialize_app(
        cred, {"storageBucket": st.secrets["firebase"]["storage_bucket"]}
    )


def get_db():
    get_app()
    return firestore.client()


def get_bucket():
    get_app()
    return storage.bucket()


def web_api_key() -> str:
    return st.secrets["firebase"]["web_api_key"]
