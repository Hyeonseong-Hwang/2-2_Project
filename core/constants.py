"""역할(Role)과 케이스 상태(Status), 상태 전이 규칙을 한곳에서 관리합니다.

담당: 파트 A (인증·DB)
이 파일의 값은 팀 전체가 같이 쓰므로, 바꿀 때는 반드시 PR로 리뷰를 받습니다.
"""

# ── 사용자 역할 ──────────────────────────────────────────────
ROLE_REGISTRAR = "registrar"   # 등록 담당자: 케이스·영상 접수
ROLE_REVIEWER = "reviewer"     # 검토 담당자: 처리·비교·메모·완료
ROLE_ADMIN = "admin"           # 관리 담당자: 배정·진행 현황

ROLE_LABELS = {
    ROLE_REGISTRAR: "등록 담당자",
    ROLE_REVIEWER: "검토 담당자",
    ROLE_ADMIN: "관리자",
}

# 회원가입 직후 기본 역할. 관리자는 Firestore 콘솔에서 users/{uid}.role 을 직접 바꿉니다.
DEFAULT_ROLE = ROLE_REVIEWER

# ── 케이스 상태 ──────────────────────────────────────────────
STATUS_RECEIVED = "received"       # 접수
STATUS_ASSIGNED = "assigned"       # 배정
STATUS_IN_REVIEW = "in_review"     # 검토 중
STATUS_DONE = "done"               # 완료

STATUS_LABELS = {
    STATUS_RECEIVED: "접수",
    STATUS_ASSIGNED: "배정",
    STATUS_IN_REVIEW: "검토 중",
    STATUS_DONE: "완료",
}

# ── 상태 전이 규칙: (현재 상태, 다음 상태) -> 실행할 수 있는 역할 ──
# 보고서의 상태전이도와 반드시 같은 내용이어야 합니다.
TRANSITIONS = {
    (STATUS_RECEIVED, STATUS_ASSIGNED): {ROLE_ADMIN},                  # 담당자 배정
    (STATUS_ASSIGNED, STATUS_IN_REVIEW): {ROLE_REVIEWER},              # 검토 시작 (배정된 본인만)
    (STATUS_IN_REVIEW, STATUS_DONE): {ROLE_REVIEWER},                  # 검토 완료 (배정된 본인만)
    (STATUS_IN_REVIEW, STATUS_ASSIGNED): {ROLE_ADMIN},                 # 보완 후 재배정
    (STATUS_DONE, STATUS_IN_REVIEW): {ROLE_ADMIN},                     # 완료 후 수정 (이력 필수)
}

# 배정된 본인만 할 수 있는 전이
ASSIGNEE_ONLY = {
    (STATUS_ASSIGNED, STATUS_IN_REVIEW),
    (STATUS_IN_REVIEW, STATUS_DONE),
}

# ── 업로드 허용 형식 ─────────────────────────────────────────
ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "dcm"]
MAX_UPLOAD_MB = 50
