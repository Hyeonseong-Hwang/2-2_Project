"""pydicom에 내장된 예제 DICOM 영상 목록.  담당: 파트 B·C

인터넷 연결이나 다운로드 없이 pydicom 설치만으로 쓸 수 있는 연습용 영상입니다.
크기가 작아서(CT 128×128) 개발·테스트용으로만 쓰고, 시연용은 IDC 등 공개 데이터로 바꿉니다.
출처: pydicom 테스트 데이터 (pydicom.examples)
"""

from io import BytesIO

from pydicom import examples

# 화면에 보여줄 이름 -> pydicom.examples 의 속성 이름
SAMPLES = {
    "CT (128×128, 척추 단면)": "ct",
    "MR (64×64)": "mr",
    "MR 큰 영상 (300×484)": "overlay",
    "초음파 컬러 (240×320)": "rgb_color",
}


def sample_bytes(label: str) -> bytes:
    """예제 영상을 .dcm 파일 바이트로 돌려줍니다. imaging.io.load_image 에 그대로 넣을 수 있습니다."""
    ds = getattr(examples, SAMPLES[label])
    buf = BytesIO()
    ds.save_as(buf)
    return buf.getvalue()
