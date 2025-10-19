import logging
from main import setup_logging


def test_setup_logging_capability(caplog):
    setup_logging()
    logging.getLogger('test').info('hello')
    assert True  # smoke test: ensures no exceptions
