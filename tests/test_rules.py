"""상태 전이·권한 규칙 자동화 테스트. 실행: uv run pytest"""

import pytest

from core.constants import (ROLE_ADMIN, ROLE_REGISTRAR, ROLE_REVIEWER, STATUS_ASSIGNED,
                            STATUS_DONE, STATUS_IN_REVIEW, STATUS_RECEIVED)
from core.rules import PermissionDenied, check_transition


def test_admin_can_assign():
    check_transition(STATUS_RECEIVED, STATUS_ASSIGNED, ROLE_ADMIN, "admin1", None)


def test_registrar_cannot_assign():
    with pytest.raises(PermissionDenied):
        check_transition(STATUS_RECEIVED, STATUS_ASSIGNED, ROLE_REGISTRAR, "reg1", None)


def test_assignee_can_start_review():
    check_transition(STATUS_ASSIGNED, STATUS_IN_REVIEW, ROLE_REVIEWER, "rev1", "rev1")


def test_other_reviewer_cannot_start_review():
    with pytest.raises(PermissionDenied):
        check_transition(STATUS_ASSIGNED, STATUS_IN_REVIEW, ROLE_REVIEWER, "rev2", "rev1")


def test_cannot_skip_to_done():
    with pytest.raises(PermissionDenied):
        check_transition(STATUS_RECEIVED, STATUS_DONE, ROLE_ADMIN, "admin1", None)


def test_reopen_done_only_admin():
    check_transition(STATUS_DONE, STATUS_IN_REVIEW, ROLE_ADMIN, "admin1", "rev1")
    with pytest.raises(PermissionDenied):
        check_transition(STATUS_DONE, STATUS_IN_REVIEW, ROLE_REVIEWER, "rev1", "rev1")
