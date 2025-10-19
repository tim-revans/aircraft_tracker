import pytest
from utils.geo_utils import distance_km


def test_distance_km_zero():
    a = (0.0, 0.0)
    b = (0.0, 0.0)
    assert distance_km(a, b) == pytest.approx(0.0, abs=1e-6)


def test_distance_km_known():
    # Distance between Paris (48.8566,2.3522) and London (51.5074,-0.1278) ~343 km
    paris = (48.8566, 2.3522)
    london = (51.5074, -0.1278)
    d = distance_km(paris, london)
    assert 330 < d < 360
