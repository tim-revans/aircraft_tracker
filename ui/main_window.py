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

        # Map view: create a lightweight placeholder now (safe in headless
        # environments). We will lazily create a real QWebEngineView only when
        # rendering a map inside `refresh()`; that creation is wrapped in
        # try/except to avoid native crashes in restricted environments.
        self.web_view = QWidget()
        # Provide a no-op load method so code calling `.load()` is safe
        self.web_view.load = lambda *a, **k: None  # type: ignore

        # Keep a reference to the main layout so we can replace the placeholder
        # with a real web view later if creation succeeds.
        self._main_layout = layout
        self._web_view_index = self._main_layout.count()
        self._main_layout.addWidget(self.web_view, 3)

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

        # Render map and load into web view. We lazily construct QWebEngineView
        # here if available; creation can fail in headless CI so wrap in
        # try/except and keep the placeholder as a safe fallback.
        try:
            m = create_map(center_lat, center_lon, zoom_start=8)
            m = add_aircraft_markers(m, aircraft, highlight_radius_km=50)
            out_path = os.path.join(tempfile.gettempdir(), "aircraft_map.html")
            m.save(out_path)

            # If a real QWebEngineView is available and not yet created, try
            # to create it and replace the placeholder in the layout.
            if QWebEngineView is not None and not isinstance(self.web_view, QWebEngineView):
                try:
                    real_view = QWebEngineView()
                    # Replace placeholder with real web view in the layout
                    self._main_layout.removeWidget(self.web_view)
                    self.web_view.deleteLater()
                    self.web_view = real_view
                    self._main_layout.insertWidget(self._web_view_index, self.web_view, 3)
                except Exception:
                    logger.exception("Failed to create QWebEngineView; continuing with placeholder")

            # Load the local file into whichever web_view we have (real or placeholder)
            try:
                self.web_view.load(QUrl.fromLocalFile(out_path))
            except Exception:
                # If placeholder or load fails, ignore — label update matters most for tests
                logger.exception("Failed to load map into web view")
        except Exception:
            logger.exception("Failed to render map")
