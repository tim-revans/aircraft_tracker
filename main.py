"""Entry point for the Aircraft Tracker app.

This file will initialize logging, create the Qt application, and load the main window.
"""
import sys
import logging

from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow


"""Entry point for the Aircraft Tracker application.

This module exposes a minimal setup function for logging and a main()
function to start the Qt event loop. Kept minimal so tests can import
`setup_logging` without side-effects.
"""


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main():
    setup_logging()
    logging.info("Starting Aircraft Tracker")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
