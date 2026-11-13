"""로그인이 어느 단계에서 멈추는지 확인하는 진단 스크립트.

실행: uv run python debug_login.py 이메일 비밀번호
확인이 끝나면 이 파일은 지워도 됩니다. (Git에 올리지 않아도 됨)
"""

import sys
import time
import tomllib

import requests

email, password = sys.argv[1], sys.argv[2]
secrets = tomllib.load(open(".streamlit/secrets.toml", "rb"))


def step(name):
    print(f"\n[{name}] 시작...", flush=True)
    return time.time()


# 1단계: Firebase Auth REST API로 비밀번호 확인
t = step("1단계 비밀번호 확인 (Firebase Auth REST)")
res = requests.post(
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    f"?key={secrets['firebase']['web_api_key']}",
    json={"email": email, "password": password, "returnSecureToken": True},
    timeout=15,
)
data = res.json()
if "error" in data:
    sys.exit(f"  실패: {data['error'].get('message')}")
print(f"  성공 ({time.time() - t:.1f}초) uid={data['localId']}")

# 2단계: firebase-admin 초기화 + 토큰 검증
import firebase_admin
from firebase_admin import auth, credentials, firestore

t = step("2단계 서비스 계정 키로 토큰 검증")
cred = credentials.Certificate(dict(secrets["firebase_service_account"]))
firebase_admin.initialize_app(cred)
decoded = auth.verify_id_token(data["idToken"])
print(f"  성공 ({time.time() - t:.1f}초) project={cred.project_id}")

# 3단계: Firestore에서 users/{uid} 읽기
t = step("3단계 Firestore users 문서 읽기")
doc = firestore.client().collection("users").document(decoded["uid"]).get(timeout=15)
print(f"  성공 ({time.time() - t:.1f}초) 문서 존재={doc.exists} 내용={doc.to_dict()}")

print("\n세 단계 모두 통과했습니다.")
