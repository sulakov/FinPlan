from PyQt5.QtWidgets import (
    QGroupBox, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QDateEdit, QSizePolicy,
    QGridLayout, QLineEdit
)
from PyQt5.QtCore import Qt

"""
Input panel on the left side of the main window.
UI elements to: 
select planning period
enter expenses and income for three months
control scenario, navigation and data actions
"""

class InputPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedWidth(600)

        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Title label
        title = QLabel("💰 FinPlan – Financial Planner")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(40)
        layout.addWidget(title)

        # Top control row (period, scenario, exit)
        layout.addWidget(self._create_top_row())

        # Month selection buttons
        month_box = QGroupBox("Select Month")
        mb_layout = QHBoxLayout(month_box)
        self.month_buttons = [QPushButton(f"Month {i}", checkable=True) for i in (1, 2, 3)]
        for btn in self.month_buttons:
            mb_layout.addWidget(btn)
        layout.addWidget(month_box)

        # Bottom layout: expenses and income input blocks
        bottom = QWidget()
        b_layout = QHBoxLayout(bottom)
        b_layout.setSpacing(15)
        bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(bottom)

        # Expense input group
        self.exp_group = QGroupBox("Expenses Input")
        self.exp_layout = QVBoxLayout(self.exp_group)
        b_layout.addWidget(self.exp_group, 1)

        # Expense input grid
        self.exp_grid = QGridLayout()
        self._setup_grid(self.exp_grid)
        self.exp_inputs = []
        self.exp_group.setLayout(self.exp_layout)

        # Expense container widget
        self.exp_container = QWidget()
        self.exp_container.setLayout(self.exp_grid)
        self.exp_layout.addWidget(self.exp_container)

        # Submit expenses button
        self.submitExpensesBtn = QPushButton("Submit Expenses", objectName="submitExpensesBtn")
        self.exp_layout.addWidget(self.submitExpensesBtn, alignment=Qt.AlignCenter)

        # Income input group
        self.inc_group = QGroupBox("Income Input")
        self.inc_layout = QVBoxLayout(self.inc_group)
        b_layout.addWidget(self.inc_group, 1)

        # Guaranteed income grid
        self.inc_guar_grid = QGridLayout()
        self._setup_grid(self.inc_guar_grid)
        self.inc_guar_inputs = []
        guar_box = QGroupBox("Guaranteed Income")
        guar_box.setLayout(self.inc_guar_grid)
        self.inc_layout.addWidget(guar_box)

        # Expected income grid
        self.inc_exp_grid = QGridLayout()
        self._setup_grid(self.inc_exp_grid)
        self.inc_exp_inputs = []
        exp_box = QGroupBox("Expected Income")
        exp_box.setLayout(self.inc_exp_grid)
        self.inc_layout.addWidget(exp_box)

        # Submit income button
        self.submitIncomeBtn = QPushButton("Submit Income", objectName="submitIncomeBtn")
        self.inc_layout.addWidget(self.submitIncomeBtn, alignment=Qt.AlignCenter)

    # Top row: period controls, scenario selection, period shift, exit
    def _create_top_row(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(120)
        layout = QHBoxLayout(w)
        layout.setSpacing(10)

        # Start month selector
        box1 = QGroupBox("Select Start Month")
        l1 = QVBoxLayout(box1)
        self.start_label = QLabel("Choose month")
        self.start_label.setAlignment(Qt.AlignCenter)
        l1.addWidget(self.start_label)
        self.startDateEdit = QDateEdit(calendarPopup=True)
        self.startDateEdit.setDisplayFormat("MMMM yyyy")
        l1.addWidget(self.startDateEdit)
        self.confirmMonthBtn = QPushButton("Confirm", objectName="confirmMonthBtn")
        l1.addWidget(self.confirmMonthBtn)
        layout.addWidget(box1)

        # Output and scenario control
        box2 = QGroupBox("Output Control")
        l2 = QVBoxLayout(box2)
        self.refreshOutputBtn = QPushButton("Refresh Data", objectName="refreshOutputBtn")
        self.changeScenarioBtn = QPushButton("Change Scenario", objectName="changeScenarioBtn")
        l2.addWidget(self.refreshOutputBtn)
        l2.addWidget(self.changeScenarioBtn)
        self.scenario_label = QLabel("Select scenario")
        self.scenario_label.setAlignment(Qt.AlignCenter)
        l2.addWidget(self.scenario_label)
        layout.addWidget(box2)

        # Period shift buttons
        box3 = QGroupBox("Month Closing")
        l3 = QVBoxLayout(box3)
        self.nextPeriodBtn = QPushButton("Move Period Forward", objectName="nextPeriodBtn")
        self.recalcPeriodBtn = QPushButton("Recalculate Period", objectName="recalcPeriodBtn")
        l3.addWidget(self.nextPeriodBtn)
        l3.addWidget(self.recalcPeriodBtn)
        layout.addWidget(box3)

        # Save and reset actions
        box4 = QGroupBox("Exit")
        l4 = QVBoxLayout(box4)
        self.saveExitBtn = QPushButton("Save and Exit", objectName="saveExitBtn")
        self.clearDataBtn = QPushButton("Erase All Data and Restart", objectName="clearDataBtn")
        l4.addWidget(self.saveExitBtn, alignment=Qt.AlignCenter)
        l4.addWidget(self.clearDataBtn, alignment=Qt.AlignCenter)
        layout.addWidget(box4)

        return w

    # Setup layout properties for input grids
    def _setup_grid(self, grid):
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 0)

    # Fill grids
    
    def set_expense_items(self, items: list[str], input_width: int):
        self._set_items_in_grid(self.exp_grid, items, input_width, self.exp_inputs)
        
    def set_income_items(self, guaranteed: list[str], expected: list[str], input_width: int):
        self._set_items_in_grid(self.inc_guar_grid, guaranteed, input_width, self.inc_guar_inputs)
        self._set_items_in_grid(self.inc_exp_grid, expected, input_width, self.inc_exp_inputs)

    # Populate a grid with labeled input fields
    def _set_items_in_grid(self, grid, items: list[str], input_width: int, target_list: list):
        for i in reversed(range(grid.count())):
            widget = grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        target_list.clear()
        for row, name in enumerate(items):
            lbl = QLabel(name)
            lbl.setWordWrap(True)
            inp = QLineEdit()
            inp.setFixedWidth(input_width)
            grid.addWidget(lbl, row, 0, alignment=Qt.AlignLeft)
            grid.addWidget(inp, row, 1, alignment=Qt.AlignRight)
            target_list.append(inp)

    # Set labels for month buttons
    def set_month_buttons_labels(self, labels: list[str]):
        for btn, lbl in zip(self.month_buttons, labels):
            btn.setText(lbl)
        if labels:
            self.start_label.setText(labels[0])

    # Uncheck all month buttons
    def clear_month_buttons_selection(self):
        for btn in self.month_buttons:
            btn.setChecked(False)

    # Enable or disable date selector and month buttons
    def enable_date_selection(self, enabled: bool):
        self.startDateEdit.setEnabled(enabled)
        self.confirmMonthBtn.setEnabled(enabled)

    def enable_month_buttons(self, enabled: bool):
        for btn in self.month_buttons:
            btn.setEnabled(enabled)

    # Return widgets
    
    def get_expense_inputs(self):
        return self.exp_inputs

    def get_income_inputs(self):
        return self.inc_guar_inputs + self.inc_exp_inputs

    # Clear all fields
    
    def clear_expense_inputs(self):
        for w in self.exp_inputs:
            w.clear()

    def clear_income_inputs(self):
        for w in self.inc_guar_inputs + self.inc_exp_inputs:
            w.clear()

    # Set values into fields
    
    def set_expense_values(self, values: dict[str, str]):
        for name, widget in zip(values, self.exp_inputs):
            widget.setText(str(values.get(name, "")))

    def set_income_values(self, values: dict[str, str]):
        all_widgets = self.inc_guar_inputs + self.inc_exp_inputs
        for name, widget in zip(values, all_widgets):
            widget.setText(str(values.get(name, "")))