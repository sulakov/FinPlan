from PyQt5.QtWidgets import (
    QGroupBox, QWidget, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QTableWidget, QTableWidgetItem, QLayout
)
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class OutputPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedWidth(900)  # расширенная ширина

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Верхняя часть: две таблицы в горизонтальном layout
        top_tables = QWidget()
        top_layout = QHBoxLayout(top_tables)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        # Таблица с данными
        self.entries_group = QGroupBox("Forecast Data")
        entries_layout = QVBoxLayout(self.entries_group)
        entries_layout.setContentsMargins(5, 5, 5, 5)
        self.entries_table = QTableWidget()
        self.entries_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        entries_layout.addWidget(self.entries_table)
        top_layout.addWidget(self.entries_group, stretch=2)  # 2 части из 4


        # Таблица прогнозных метрик
        self.forecast_group = QGroupBox("Forecast Metrics")
        forecast_layout = QVBoxLayout(self.forecast_group)
        self.forecast_table = QTableWidget()
        self.forecast_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        forecast_layout.addWidget(self.forecast_table)
        top_layout.addWidget(self.forecast_group, stretch=2) # 2 части из 4

        main_layout.addWidget(top_tables)

        # Нижняя часть: графики вертикально
        bottom = QWidget()
        bottom_layout = QVBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(5)
        bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Ограничиваем высоту групп с графиками
        self.chart_group1 = QGroupBox("Net Cash Flow")
        self.chart_group1.setMaximumHeight(200)
        chart1_layout = QVBoxLayout(self.chart_group1)
        chart1_layout.setContentsMargins(10, 0, 10, 0)
        self.figure1 = Figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.canvas1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas1.setFixedHeight(160)
        chart1_layout.addWidget(self.canvas1)
        bottom_layout.addWidget(self.chart_group1)

        self.chart_group2 = QGroupBox("Runway Forecast")
        self.chart_group2.setMaximumHeight(200)
        chart2_layout = QVBoxLayout(self.chart_group2)
        chart2_layout.setContentsMargins(10, 0, 10, 0)
        self.figure2 = Figure()
        self.canvas2 = FigureCanvas(self.figure2)
        self.canvas2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas2.setFixedHeight(160)
        chart2_layout.addWidget(self.canvas2)
        bottom_layout.addWidget(self.chart_group2)

        main_layout.addWidget(bottom)

        # Распределение пространства между таблицами и графиками
        main_layout.setStretchFactor(top_tables, 2)
        main_layout.setStretchFactor(bottom, 1)

    def set_entries_data(self, headers: list[str], data: list[list]):
        self.entries_table.clear()
        self.entries_table.setColumnCount(len(headers))
        self.entries_table.setHorizontalHeaderLabels(headers)
        self.entries_table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.entries_table.setItem(i, j, item)
        self.entries_table.resizeColumnsToContents()

    def set_forecast_data(self, headers: list[str], data: list[list[str]]):
        self.forecast_table.clear()
        self.forecast_table.setColumnCount(len(headers))
        self.forecast_table.setHorizontalHeaderLabels(headers)
        self.forecast_table.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.forecast_table.setItem(i, j, item)

        self.forecast_table.resizeColumnsToContents()
        self.forecast_table.resizeRowsToContents()