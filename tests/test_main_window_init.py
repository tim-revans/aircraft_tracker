from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow


def ensure_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


@patch('services.data_fetcher.fetch_states')
@patch('utils.geo_utils.get_current_location')
def test_main_window_calls_refresh_on_init(mock_get_loc: MagicMock, mock_fetch_states: MagicMock):
    """This test asserts that MainWindow.refresh() is executed during __init__
    so the info label is populated immediately. It patches network/geolocation
    calls to deterministic values."""
    ensure_qapp()

    # Provide a fixed location and a single nearby aircraft
    mock_get_loc.return_value = (48.0, 2.0)
    mock_fetch_states.return_value = {
        'time': 0,
        'states': [["abc123", "CALL123", "Country", None, None, 2.1, 48.1, None, False, None, None, None, None, None, None, None, None]]
    }

    win = MainWindow()

    # After initialization (and expected internal refresh), the info label
    # should not contain the placeholder text.
    assert "Nearest aircraft info will appear here." not in win.info_label.text()
