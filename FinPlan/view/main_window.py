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

# Ширина полей ввода, используется в InputPanel
INPUT_FIELD_WIDTH = 120

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = None

        self.setWindowTitle("FinPlan – Main Window")
        self.setGeometry(100, 100, 1600, 700)
        self.setMinimumSize(1300, 700)
        # фон и прочее теперь из style.qss
        # self.setStyleSheet("background-color: white;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(30)

        # Создаём панели
        self.input_panel = InputPanel(self)
        self.output_panel = OutputPanel(self)
        layout.addWidget(self.input_panel)
        layout.addWidget(self.output_panel)

        # --- объём: навешиваем drop-shadow на панели ---
        for panel in (self.input_panel, self.output_panel):
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)               # сила размытия
            shadow.setOffset(0, 4)                # смещение тени по X и Y
            shadow.setColor(QColor(0, 0, 0, 80))  # полупрозрачная чёрная тень
            panel.setGraphicsEffect(shadow)
        # -------------------------------------------------

        # Заполняем панели списками из модели
        self.input_panel.set_expense_items(
            DEFAULT_EXPENSE_CATEGORIES,
            INPUT_FIELD_WIDTH
        )
        self.input_panel.set_income_items(
            DEFAULT_INCOME_GUARANTEED_CATEGORIES,
            DEFAULT_INCOME_EXPECTED_CATEGORIES,
            INPUT_FIELD_WIDTH
        )

        # Привязываем контроллер
        self.set_controller(FinController(self))

    def set_controller(self, controller):
        """
        Привязывает контроллер к View и настраивает сигналы.
        """
        self.controller = controller
        # Пример подключения сигналов (зависит от реализации InputPanel):
        # self.input_panel.expense_added.connect(controller.add_expense)
        # self.input_panel.income_added.connect(controller.add_income)
        # self.input_panel.forecast_requested.connect(controller.generate_forecast)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Подгружаем внешний QSS из папки resources
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    qss_path = os.path.join(project_dir, "resources", "style.qss")
    if os.path.isfile(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: не найден файл стилей по пути: {qss_path}")

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())