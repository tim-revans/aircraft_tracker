"""Utilities to fetch aircraft images from Wikimedia/Wikipedia APIs."""

import logging
import requests
from PIL import Image
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)


def fetch_aircraft_image(query: str) -> Optional[Image.Image]:
    """Attempt to fetch an aircraft image given a query string.

    The function queries the MediaWiki API for page images and, if an
    original image URL is found, downloads and returns it as a PIL Image.

    Args:
        query: Search string (callsign or model name).

    Returns:
        A PIL Image on success, or None on failure.
    """
    try:
        # Wikimedia search
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'pageimages',
            'pilicense': 'any',
            'piprop': 'original',
            'titles': query,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        pages = data.get('query', {}).get('pages', {})
        for page in pages.values():
            orig = page.get('original')
            if orig and orig.get('source'):
                img_url = orig['source']
                logger.info(f"Fetching image for {query} from {img_url}")
                r2 = requests.get(img_url, timeout=10)
                r2.raise_for_status()
                return Image.open(BytesIO(r2.content))
    except Exception as e:
        logger.error(f"Failed to fetch image for {query}: {e}")
    return None
