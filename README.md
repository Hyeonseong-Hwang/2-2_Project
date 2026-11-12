# 교육용 웹 PACS

초급프로젝트 PBL 텀프로젝트. 공개 데이터와 모의 케이스로 작동하는 교육용 의료영상 저장·조회·처리·검토 시스템입니다.
실제 진단에 사용할 수 없습니다.

- 스택: Python · Streamlit · Firebase Authentication · Cloud Firestore · Firebase Storage · JCloud
- 지원 형식: PNG, JPG, DICOM(.dcm, 파일 읽기만 지원 / DICOM 네트워크 통신은 범위 밖)

## 폴더 구조

```
web-pacs/
├─ app.py                 앱 시작점, 로그인·역할별 메뉴
├─ core/                  [파트 A] 인증·DB·권한
│  ├─ constants.py        역할, 상태, 상태 전이 규칙 (팀 공용, 수정 시 PR 필수)
│  ├─ rules.py            권한·상태 검사 (순수 함수, 테스트 대상)
│  ├─ firebase.py         Firebase 연결
│  ├─ auth.py             로그인·회원가입·로그아웃
│  └─ db.py               Firestore 읽기·쓰기 (화면에서는 이 함수만 사용)
├─ imaging/               [파트 B·C] 영상 처리 로직 (Streamlit 의존 없음)
│  ├─ io.py               [B] PNG/JPG/DICOM 읽기, Window/Level
│  ├─ algorithms.py       [C] 영상처리 알고리즘 3종
│  └─ roi.py              [C] ROI 통계
├─ views/                 화면 (Streamlit 페이지)
│  ├─ cases.py            [A·B] 케이스 목록
│  ├─ register.py         [A·B] 케이스 등록 (등록 담당자·관리자)
│  ├─ viewer.py           [B] 영상 뷰어
│  ├─ processing.py       [C] 영상처리·ROI
│  ├─ feature.py          [D] 특화 기능
│  └─ admin.py            [A·D] 배정·진행 현황 (관리자)
└─ tests/                 자동화 테스트 (uv run pytest)
```

원칙: 계산 로직은 `core/rules.py`, `imaging/`에, 화면은 `views/`에 둡니다. 로직을 화면과 분리해야 pytest로 테스트할 수 있습니다.

## 처음 실행하기

```bash
git clone <저장소 주소>
cd web-pacs
uv sync
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # 값은 팀장에게 따로 받기
uv run streamlit run app.py
```

테스트:

```bash
uv run pytest
```

## Firebase 설정 (팀장 1회)

1. Firebase 콘솔에서 프로젝트 생성
2. Authentication → 로그인 방법 → 이메일/비밀번호 사용 설정
3. Firestore Database 생성
4. Storage 생성
5. 프로젝트 설정 → 일반 → 웹 API 키 복사 / 서비스 계정 → 새 비공개 키 생성
6. 위 값을 `.streamlit/secrets.toml`에 입력
7. 관리자 계정: 회원가입 후 Firestore `users/{uid}` 문서의 `role`을 `admin`으로 직접 변경

## 역할과 상태

| 역할 | 할 수 있는 일 |
| --- | --- |
| registrar (등록 담당자) | 케이스·영상 등록 |
| reviewer (검토 담당자) | 배정받은 케이스의 검토 시작·처리·메모·완료 |
| admin (관리자) | 배정, 재배정, 완료 후 수정, 진행 현황 |

상태: 접수 → 배정 → 검토 중 → 완료 (검토 중 → 배정: 보완 재배정 / 완료 → 검토 중: 관리자 수정). 규칙은 `core/constants.py`의 `TRANSITIONS`.

## 협업 규칙

- `main`에 직접 push 금지. 작업마다 Issue 생성 → 브랜치 → PR → 다른 팀원 리뷰 1명 이상 → 병합
- 브랜치 이름: `feat/A-login`, `feat/B-viewer`, `fix/C-roi-bounds`
- 커밋 메시지: `feat: …`, `fix: …`, `test: …`, `docs: …` + 무엇을 왜 바꿨는지
- 비밀키·실제 환자 데이터는 절대 커밋하지 않기

## 데이터 출처

| 데이터 | 출처 | 이용 조건 |
| --- | --- | --- |
| pydicom 예제 CT | pydicom 라이브러리 내장 | 테스트용 |
| (추가 예정) | | |

## AI·외부 자료 활용 기록

| 부분 | 도구·출처 | 직접 수정·검증한 내용 |
| --- | --- | --- |
| 초기 뼈대 코드 | Claude | (팀이 작성) |
