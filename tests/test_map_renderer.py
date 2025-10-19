import os
from services.map_renderer import create_map, add_aircraft_markers


def test_create_map_and_add_markers(tmp_path):
    m = create_map(48.0, 2.0, zoom_start=6)
    assert m is not None
    aircraft = [
        {'icao24': 'abc123', 'callsign': 'CALL123', 'latitude': 48.1, 'longitude': 2.1, 'distance_km': 10.0},
        {'icao24': 'def456', 'callsign': 'CALL456', 'latitude': 47.9, 'longitude': 1.9, 'distance_km': 20.0},
    ]
    m = add_aircraft_markers(m, aircraft, highlight_radius_km=50)
    out = tmp_path / "map.html"
    m.save(str(out))
    assert out.exists()
    content = out.read_text()
    assert "CALL123" in content or "abc123" in content
