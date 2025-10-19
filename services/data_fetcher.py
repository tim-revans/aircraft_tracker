"""Helpers to fetch aircraft state data from OpenSky API.

This module provides a thin wrapper around requests.get and returns the parsed
JSON response or None on error.
"""

import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

OPENSKY_URL = "https://opensky-network.org/api/states/all"


def fetch_states(bbox: Optional[Dict[str, float]] = None) -> Optional[Dict[str, Any]]:
    """Fetch raw states from OpenSky API.

    Args:
        bbox: Optional bounding box with keys 'lamin', 'lamax', 'lomin', 'lomax'.

    Returns:
        Parsed JSON response as a dict on success, or None on failure.
    """
    params = {}
    if bbox:
        params = {
            'lamin': bbox.get('lamin'),
            'lamax': bbox.get('lamax'),
            'lomin': bbox.get('lomin'),
            'lomax': bbox.get('lomax'),
        }
    try:
        logger.info("Requesting OpenSky API")
        resp = requests.get(OPENSKY_URL, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Failed to fetch OpenSky states: {e}")
        return None
