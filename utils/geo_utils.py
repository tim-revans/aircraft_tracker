from geopy.distance import geodesic
import geocoder
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def get_current_location() -> Optional[Tuple[float, float]]:
    """Use geocoder to get approximate location based on IP. Returns (lat, lon) or None."""
    try:
        g = geocoder.ip('me')
        if g.ok and g.latlng:
            logger.info(f"Detected location: {g.latlng}")
            return (g.latlng[0], g.latlng[1])
    except Exception as e:
        logger.error(f"Geolocation failed: {e}")
    return None


def distance_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return geodesic(a, b).kilometers
