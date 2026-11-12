"""영상 읽기·ROI 계산 자동화 테스트. 실행: uv run pytest"""

import cv2
import numpy as np
import pytest
from pydicom import examples

from imaging.io import apply_window, load_image
from imaging.roi import roi_stats


def test_png_roundtrip():
    img = np.full((20, 30), 100, np.uint8)
    ok, buf = cv2.imencode(".png", img)
    assert ok
    out, meta = load_image("a.png", buf.tobytes())
    assert out.shape == (20, 30) and meta["format"] == "PNG"


def test_unsupported_extension():
    with pytest.raises(ValueError):
        load_image("a.gif", b"GIF89a")


def test_broken_png():
    with pytest.raises(ValueError):
        load_image("a.png", b"not an image")


def test_dicom_sample_loads(tmp_path):
    path = tmp_path / "ct.dcm"
    examples.ct.save_as(path)
    hu, meta = load_image("ct.dcm", path.read_bytes())
    assert meta["modality"] == "CT"
    assert hu.shape == (meta["rows"], meta["cols"])


def test_window_range():
    hu = np.array([[-2000, 0, 2000]], np.float32)
    out = apply_window(hu, level=0, width=400)
    assert out.tolist() == [[0, 127, 255]]


def test_roi_stats_and_bounds():
    img = np.zeros((10, 10), np.uint8)
    img[2:4, 2:4] = 200
    s = roi_stats(img, 2, 2, 4, 4, pixel_spacing=[0.5, 0.5])
    assert s["mean"] == 200 and s["area_px"] == 4 and s["area_mm2"] == 1.0
    with pytest.raises(ValueError):
        roi_stats(img, 5, 5, 20, 20)
