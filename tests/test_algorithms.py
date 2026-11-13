"""알고리즘 자동화 테스트. 실행: uv run pytest"""

import numpy as np
import pytest

from imaging import algorithms as alg
from imaging.io import load_image
from imaging.samples import SAMPLES, sample_bytes


@pytest.fixture
def gray():
    img = np.zeros((64, 64), np.uint8)
    img[16:48, 16:48] = 200                      # 가운데 밝은 사각형
    rng = np.random.default_rng(0)
    noisy = img.astype(int) + rng.normal(0, 10, img.shape)
    return np.clip(noisy, 0, 255).astype(np.uint8)


def test_original_not_modified(gray):
    before = gray.copy()
    alg.clahe(gray); alg.bilateral(gray); alg.otsu(gray); alg.canny(gray)
    assert np.array_equal(gray, before)


def test_otsu_separates_square(gray):
    mask, th = alg.otsu(gray)
    assert 20 < th < 180          # 배경(0 근처)과 사각형(200) 사이 어딘가
    assert mask[32, 32] == 255 and mask[2, 2] == 0


def test_bilateral_reduces_noise(gray):
    out = alg.bilateral(gray)
    assert out[20:44, 20:44].std() < gray[20:44, 20:44].std()


def test_canny_finds_edges_only_at_border(gray):
    edges = alg.canny(alg.bilateral(gray), 50, 150)
    assert edges[16, 30] == 255 or edges[15, 30] == 255 or edges[17, 30] == 255
    assert edges[32, 32] == 0


def test_invalid_params(gray):
    with pytest.raises(ValueError):
        alg.canny(gray, 150, 50)
    with pytest.raises(ValueError):
        alg.clahe(np.zeros((4, 4), np.float32))


@pytest.mark.parametrize("label", list(SAMPLES))
def test_all_samples_run(label):
    image, _ = load_image("x.dcm", sample_bytes(label))
    g = alg.to_uint8(image)
    assert g.ndim == 2 and g.dtype == np.uint8
    for f in (alg.clahe, alg.bilateral, alg.canny):
        assert f(g).shape == g.shape
