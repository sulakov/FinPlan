import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from .input_panel import InputPanel
from .output_panel import OutputPanel

from ..model.constants import (
    DEFAULT_EXPENSE_CATEGORIES,
    DEFAULT_INCOME_GUARANTEED_CATEGORIES,
    DEFAULT_INCOME_EXPECTED_CATEGORIES,
)
from ..controller.fin_controller import FinController

"""
Main application window that combines input and output panels,
initializes layout, styles, and controller.
"""

# Input field width, used in InputPanel
INPUT_FIELD_WIDTH = 120

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = None

        self.setWindowTitle("FinPlan – Main Window")
        self.setGeometry(100, 100, 1600, 700)
        self.setMinimumSize(1300, 700)
        # Background and other styles now come from style.qss
        # self.setStyleSheet("background-color: white;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(30)

        # Create main panels
        self.input_panel = InputPanel(self)
        self.output_panel = OutputPanel(self)
        layout.addWidget(self.input_panel)
        layout.addWidget(self.output_panel)

        # Add drop shadow effect to panels
        for panel in (self.input_panel, self.output_panel):
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)               # Blur radius
            shadow.setOffset(0, 4)                # Shadow offset on X and Y axes
            shadow.setColor(QColor(0, 0, 0, 80))  # Semi-transparent black shadow
            panel.setGraphicsEffect(shadow)

        # Populate panels with category lists from model
        self.input_panel.set_expense_items(
            DEFAULT_EXPENSE_CATEGORIES,
            INPUT_FIELD_WIDTH
        )
        self.input_panel.set_income_items(
            DEFAULT_INCOME_GUARANTEED_CATEGORIES,
            DEFAULT_INCOME_EXPECTED_CATEGORIES,
            INPUT_FIELD_WIDTH
        )

        # Bind controller to the view
        self.controller = FinController(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load external QSS stylesheet from resources folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    qss_path = os.path.join(project_dir, "resources", "style.qss")
    if os.path.isfile(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: style file not found at path: {qss_path}")

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())