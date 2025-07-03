from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt


class ExpensesSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inputs_by_month = {}  # {0: {категория: QLineEdit}}
        self.categories = []

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        # Верхняя строка: Заголовок + Submit
        header = QHBoxLayout()
        header.addWidget(QLabel("Expenses"))
        self.submit_button = QPushButton("Submit Expenses")
        self.submit_button.setObjectName("submitExpensesBtn")
        header.addWidget(self.submit_button)
        self.layout.addLayout(header)

    def set_items(self, categories: list[str], input_width: int):
        """Инициализация полей ввода"""
        self.categories = categories
        # Удаляем старые виджеты (если были)
        while self.layout.count() > 1:
            item = self.layout.takeAt(1)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        self.inputs_by_month.clear()

        for month_idx in range(3):
            group = QGroupBox(f"Month {month_idx + 1}")
            g_layout = QVBoxLayout(group)
            fields = {}
            for cat in categories:
                row = QHBoxLayout()
                row.addWidget(QLabel(cat))
                field = QLineEdit()
                field.setFixedWidth(input_width)
                field.setAlignment(Qt.AlignRight)
                row.addWidget(field)
                g_layout.addLayout(row)
                fields[cat] = field
            self.inputs_by_month[month_idx] = fields
            self.layout.addWidget(group)

    def get_data(self, month_idx: int) -> dict[str, str]:
        return {
            cat: widget.text().strip()
            for cat, widget in self.inputs_by_month[month_idx].items()
        }

    def set_data(self, month_idx: int, values: dict[str, str]):
        for cat, widget in self.inputs_by_month[month_idx].items():
            widget.setText(str(values.get(cat, "")))

    def clear(self):
        for fields in self.inputs_by_month.values():
            for field in fields.values():
                field.clear()