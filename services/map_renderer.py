import folium
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def create_map(center_lat: float, center_lon: float, zoom_start: int = 8) -> folium.Map:
    """Create and return a Folium map centered at the given coordinates.

    Args:
        center_lat: Latitude of the map center.
        center_lon: Longitude of the map center.
        zoom_start: Initial zoom level.

    Returns:
        A folium.Map instance.
    """
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
    return m


def add_aircraft_markers(m: folium.Map, aircraft: List[Dict[str, Any]], highlight_radius_km: float) -> folium.Map:
    """Add markers for aircraft to the given folium map and draw a highlight circle.

    The aircraft list is expected to contain dicts with keys: 'latitude', 'longitude',
    'callsign' or 'icao24', and optionally 'distance_km'. Missing lat/lon entries are
    ignored.

    Returns the modified map object for convenience.
    """
    for ac in aircraft:
        lat = ac.get('latitude')
        lon = ac.get('longitude')
        if lat is None or lon is None:
            continue
        popup = folium.Popup(f"{ac.get('callsign') or ac.get('icao24')}\n{ac.get('distance_km', '?')} km", parse_html=True)
        folium.CircleMarker(location=[lat, lon], radius=5, popup=popup, color='blue').add_to(m)
    # Draw highlight circle around the map center
    try:
        center = getattr(m, 'location', None) or [0.0, 0.0]
        folium.Circle(location=center, radius=highlight_radius_km * 1000, color='red', fill=False).add_to(m)
    except Exception:
        logger.debug("Could not draw highlight circle", exc_info=True)
    return m
