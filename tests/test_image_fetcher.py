from services.image_fetcher import fetch_aircraft_image
from unittest.mock import patch
from PIL import Image
from io import BytesIO


def test_fetch_aircraft_image_no_result(monkeypatch):
    # Patch requests.get to return a JSON with no images
    class MockResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {'query': {'pages': {}}}

    with patch('services.image_fetcher.requests.get') as mock_get:
        mock_get.return_value = MockResp()
        img = fetch_aircraft_image('nonexistent')
        assert img is None


def test_fetch_aircraft_image_success(monkeypatch):
    # Mock two sequential requests: one for API JSON, then for image bytes
    class MockAPIResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {'query': {'pages': {'1': {'original': {'source': 'http://example.com/img.jpg'}}}}}

    class MockImgResp:
        def raise_for_status(self):
            return None

        @property
        def content(self):
            # create a tiny 1x1 PNG
            img = Image.new('RGB', (1, 1), color='white')
            b = BytesIO()
            img.save(b, format='PNG')
            return b.getvalue()

    with patch('services.image_fetcher.requests.get') as mock_get:
        mock_get.side_effect = [MockAPIResp(), MockImgResp()]
        img = fetch_aircraft_image('test')
        assert img is not None
        assert isinstance(img.size, tuple)
