"""
Entry point for the FinPlan application.
Ensures proper package setup when launched as a standalone script,
initializes the GUI, and starts the Qt event loop.
"""

import os
import sys

# If run by double-clicking (i.e. __package__ unset), add project root to sys.path
if __name__ == "__main__" and __package__ is None:
    here = os.path.dirname(__file__)        # .../project_root/FinPlan
    parent = os.path.dirname(here)          # .../project_root
    sys.path.insert(0, parent)
    __package__ = "FinPlan"

from PyQt5.QtWidgets import QApplication
from .view.main_window import MainWindow
from .controller.fin_controller import FinController

def main():
    """
    Instantiate the QApplication, create and show the main window,
    then run the Qt event loop until the app exits.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()