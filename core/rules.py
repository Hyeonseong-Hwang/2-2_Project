"""권한·상태 검사 로직. Firebase나 Streamlit에 의존하지 않는 순수 함수라서 pytest로 바로 테스트할 수 있습니다.

담당: 파트 A (인증·DB)
안내문 요구사항: "화면 표시와 별개로 실제 데이터 접근 경로에서 권한을 검사"
→ db.py의 쓰기 함수는 반드시 이 함수들을 먼저 호출합니다.
"""

from core.constants import ASSIGNEE_ONLY, TRANSITIONS


class PermissionDenied(Exception):
    """권한이 없거나 허용되지 않은 상태 변경일 때 발생합니다."""


def check_transition(current: str, nxt: str, role: str, uid: str, assignee_uid: str | None) -> None:
    """상태 변경이 허용되는지 검사합니다. 허용되지 않으면 PermissionDenied를 던집니다."""
    allowed_roles = TRANSITIONS.get((current, nxt))
    if allowed_roles is None:
        raise PermissionDenied(f"'{current}' 상태에서 '{nxt}' 상태로는 바꿀 수 없습니다.")
    if role not in allowed_roles:
        raise PermissionDenied(f"'{role}' 역할은 이 상태 변경을 할 수 없습니다.")
    if (current, nxt) in ASSIGNEE_ONLY and uid != assignee_uid:
        raise PermissionDenied("배정된 검토 담당자 본인만 할 수 있습니다.")


def require_role(role: str, *allowed: str) -> None:
    """역할 검사. 예) require_role(user_role, ROLE_ADMIN)"""
    if role not in allowed:
        raise PermissionDenied(f"이 작업은 {', '.join(allowed)} 역할만 할 수 있습니다.")
