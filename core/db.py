"""Firestore 읽기·쓰기 함수 모음. 화면(views)에서는 Firestore를 직접 부르지 말고 이 파일의 함수만 씁니다.

담당: 파트 A (인증·DB)
컬렉션 구조는 '의료영상·PACS 특강 정리' 문서의 Firestore 스키마 표를 따릅니다.
지금은 케이스·감사로그만 구현되어 있고, images / processing_runs / notes 는 TODO 입니다.
"""

from firebase_admin import firestore

from core.constants import ROLE_ADMIN, ROLE_REGISTRAR, STATUS_ASSIGNED, STATUS_RECEIVED
from core.firebase import get_db
from core.rules import check_transition, require_role


# ── 감사 추적 (누가 언제 무엇을 했는지) ───────────────────────
def log_action(user: dict, action: str, target_id: str, before=None, after=None, success=True) -> None:
    get_db().collection("audit_logs").add({
        "actor_uid": user["uid"],
        "actor_role": user["role"],
        "action": action,              # view / upload / process / status_change / note
        "target_id": target_id,
        "before": before,
        "after": after,
        "success": success,
        "at": firestore.SERVER_TIMESTAMP,
    })


# ── 케이스 ──────────────────────────────────────────────────
def create_case(user: dict, case_id: str, patient_id: str, study_date: str,
                modality: str, body_part: str) -> None:
    require_role(user["role"], ROLE_REGISTRAR, ROLE_ADMIN)
    ref = get_db().collection("cases").document(case_id)
    if ref.get().exists:
        raise ValueError(f"케이스 ID '{case_id}'가 이미 있습니다.")
    ref.set({
        "case_id": case_id,
        "patient_id": patient_id,
        "study_date": study_date,
        "modality": modality,
        "body_part": body_part,
        "status": STATUS_RECEIVED,
        "assignee_uid": None,
        "is_mock": True,
        "created_by": user["uid"],
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    })
    log_action(user, "create_case", case_id, after=STATUS_RECEIVED)


def list_cases(status: str | None = None, assignee_uid: str | None = None) -> list[dict]:
    q = get_db().collection("cases")
    if status:
        q = q.where("status", "==", status)
    if assignee_uid:
        q = q.where("assignee_uid", "==", assignee_uid)
    return [d.to_dict() for d in q.stream()]


def get_case(case_id: str) -> dict | None:
    doc = get_db().collection("cases").document(case_id).get()
    return doc.to_dict() if doc.exists else None


def change_status(user: dict, case_id: str, new_status: str, assignee_uid: str | None = None) -> None:
    """상태 변경. 권한·전이 규칙 검사 → 트랜잭션으로 저장 → 감사 로그."""
    db = get_db()
    ref = db.collection("cases").document(case_id)

    @firestore.transactional
    def _tx(tx):
        snap = ref.get(transaction=tx)
        if not snap.exists:
            raise ValueError("케이스가 없습니다.")
        case = snap.to_dict()
        check_transition(case["status"], new_status, user["role"], user["uid"], case.get("assignee_uid"))
        update = {"status": new_status, "updated_at": firestore.SERVER_TIMESTAMP}
        if new_status == STATUS_ASSIGNED:
            if not assignee_uid:
                raise ValueError("배정할 검토 담당자를 선택해야 합니다.")
            update["assignee_uid"] = assignee_uid
        tx.update(ref, update)
        return case["status"]

    try:
        before = _tx(db.transaction())
        log_action(user, "status_change", case_id, before=before, after=new_status)
    except Exception:
        log_action(user, "status_change", case_id, after=new_status, success=False)
        raise


def list_users(role: str | None = None) -> list[dict]:
    q = get_db().collection("users")
    if role:
        q = q.where("role", "==", role)
    return [d.to_dict() for d in q.stream()]


# TODO(파트 A·B): add_image, list_images  — 파일은 Storage, 위치·메타데이터는 images 컬렉션
# TODO(파트 A·C): add_processing_run      — 알고리즘·파라미터·ROI·특징값·결과 위치
# TODO(파트 A·D): add_note, list_notes    — 검토 메모·리포트, 수정 이력
