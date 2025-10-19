import pytest
from services import data_fetcher
from unittest.mock import patch


def mock_response_json():
    return {
        'time': 0,
        'states': [
            # Fields per OpenSky: icao24, callsign, origin_country, time_position, last_contact, longitude, latitude, baro_altitude, on_ground, velocity, true_track, vertical_rate, sensors, geo_altitude, squawk, spi, position_source
            ["abc123", "CALL123", "Country", None, None, 2.0, 48.0, None, False, None, None, None, None, None, None, None, None]
        ]
    }


@patch('services.data_fetcher.requests.get')
def test_fetch_states_success(mock_get):
    class MockResp:
        def raise_for_status(self):
            return None

        def json(self):
            return mock_response_json()

    mock_get.return_value = MockResp()
    data = data_fetcher.fetch_states()
    assert data is not None
    assert 'states' in data


@patch('services.data_fetcher.requests.get')
def test_fetch_states_failure(mock_get):
    mock_get.side_effect = Exception('network')
    data = data_fetcher.fetch_states()
    assert data is None
