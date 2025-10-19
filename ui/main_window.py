"""Main window UI for the Aircraft Tracker application.

This module defines the MainWindow which handles the map view and a
side panel showing nearest-aircraft information. The window exposes a
`refresh` method which is safe to call repeatedly and is connected to
an internal QTimer for periodic updates.
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer, QUrl
import os

# Avoid importing or creating Qt WebEngine in CI or when explicitly
# disabled via AIRCRAFT_TRACKER_DISABLE_WEBENGINE. Importing the
# WebEngine can initialize native processes that abort in headless
# or sandboxed environments (common on CI runners). When disabled we
# provide a lightweight placeholder with a no-op `load()` method so
# tests that only assert UI logic (like labels) can run safely.
_disable_webengine = bool(
    os.environ.get("GITHUB_ACTIONS")
    or os.environ.get("CI")
    or os.environ.get("AIRCRAFT_TRACKER_DISABLE_WEBENGINE")
)

if not _disable_webengine:
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView  # type: ignore
    except Exception:
        # Importing WebEngine failed; fall back to placeholder
        QWebEngineView = None
else:
    QWebEngineView = None

import logging
import tempfile

from services.data_fetcher import fetch_states
from services.map_renderer import create_map, add_aircraft_markers
from utils.geo_utils import get_current_location, distance_km
from typing import List, Dict, Any, Optional, Tuple

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aircraft Tracker")
        self.resize(1000, 700)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout()
        central.setLayout(layout)

        # Map view: try to create a QWebEngineView, but fall back to a
        # placeholder widget if creation fails (common in headless CI).
        if QWebEngineView is not None:
            try:
                self.web_view = QWebEngineView()
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception("QWebEngineView creation failed; using placeholder")
                self.web_view = QWidget()
                # Provide a no-op load method so code calling `.load()` is safe
                self.web_view.load = lambda *a, **k: None  # type: ignore
        else:
            logger = logging.getLogger(__name__)
            logger.info("PyQt5.QtWebEngineWidgets.QWebEngineView not available; using placeholder")
            self.web_view = QWidget()
            self.web_view.load = lambda *a, **k: None  # type: ignore

        layout.addWidget(self.web_view, 3)

        # Side panel
        side = QWidget()
        side_layout = QVBoxLayout()
        side.setLayout(side_layout)
        self.info_label = QLabel("Nearest aircraft info will appear here.")
        side_layout.addWidget(self.info_label)
        layout.addWidget(side, 1)

        # Placeholder timer to show refresh capability
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30000)

        # Perform an initial refresh so the UI shows data immediately
        try:
            self.refresh()
        except Exception:
            logger = logging.getLogger(__name__)
            logger.exception("Initial refresh failed")

    def refresh(self):
        """Fetch nearby aircraft, update the side panel with the nearest aircraft,
        render a folium map with markers and load it into the QWebEngineView."""
        logger = logging.getLogger(__name__)

        # Determine center location
        loc: Optional[Tuple[float, float]] = get_current_location()
        if loc is None:
            logger.info("Could not determine current location, defaulting to (0,0)")
            center_lat, center_lon = 0.0, 0.0
        else:
            center_lat, center_lon = loc

        # Fetch aircraft states
        data = fetch_states()
        aircraft: List[Dict[str, Any]] = []
        if data and 'states' in data and data['states']:
            for s in data['states']:
                try:
                    icao24 = s[0]
                    callsign = s[1].strip() if s[1] else None
                    lon = s[5]
                    lat = s[6]
                    if lat is None or lon is None:
                        continue
                    dist = distance_km((center_lat, center_lon), (lat, lon))
                    aircraft.append({
                        'icao24': icao24,
                        'callsign': callsign,
                        'latitude': lat,
                        'longitude': lon,
                        'distance_km': round(dist, 1),
                    })
                except Exception:
                    logger.debug("Failed to parse state entry", exc_info=True)

        # Sort by distance and update info label
        aircraft.sort(key=lambda x: x.get('distance_km', float('inf')))
        if aircraft:
            n: Dict[str, Any] = aircraft[0]
            info = f"{n.get('callsign') or n.get('icao24')} — {n.get('distance_km')} km"
        else:
            info = "No aircraft detected nearby."
        self.info_label.setText(info)

        # Render map and load into web view
        try:
            m = create_map(center_lat, center_lon, zoom_start=8)
            m = add_aircraft_markers(m, aircraft, highlight_radius_km=50)
            out_path = os.path.join(tempfile.gettempdir(), "aircraft_map.html")
            m.save(out_path)
            self.web_view.load(QUrl.fromLocalFile(out_path))
        except Exception:
            logger.exception("Failed to render or load map")
