import shutil
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QBrush, QColor
from dateutil.relativedelta import relativedelta

from ..model.fin_model import FinModel
from ..model.entry     import Entry
from ..model.category  import Category
from ..model.scenario  import Scenario
from ..model.period_shift import PeriodShiftError
from ..model.constants import (
    DEFAULT_EXPENSE_CATEGORIES,
    DEFAULT_INCOME_GUARANTEED_CATEGORIES,
    DEFAULT_INCOME_EXPECTED_CATEGORIES,
)

class FinController:
    def __init__(self, view):
        self.view  = view
        self.model = FinModel()
        view.set_controller(self)
        self._pending_shift = False
        self.expense_categories = DEFAULT_EXPENSE_CATEGORIES
        self.income_guaranteed_categories = DEFAULT_INCOME_GUARANTEED_CATEGORIES
        self.income_expected_categories = DEFAULT_INCOME_EXPECTED_CATEGORIES

        ip = view.input_panel

        # Сигналы
        ip.confirmMonthBtn.clicked.connect(self.on_confirm_period)
        ip.nextPeriodBtn.clicked.connect(self.on_prepare_period_shift)
        ip.recalcPeriodBtn.clicked.connect(self.on_recalc_period)
        ip.clearDataBtn.clicked.connect(self.on_clear_data)
        ip.refreshOutputBtn.clicked.connect(self.refresh)
        ip.scenario_label.setText("baseline")
        ip.changeScenarioBtn.clicked.connect(self.on_change_scenario)
        

        for btn in ip.month_buttons:
            btn.clicked.connect(lambda _, b=btn: self.on_select_month(b))
        ip.submitExpensesBtn.clicked.connect(self.on_submit_expenses)
        ip.submitIncomeBtn.clicked.connect(self.on_submit_incomes)

        # Инициализация в зависимости от наличия начального периода
        if self.model.period_start is None:
            # Только выбор даты
            ip.enable_date_selection(True)
            ip.confirmMonthBtn.setEnabled(True)

            # Всё остальное выключено
            ip.enable_month_buttons(False)
            ip.clear_month_buttons_selection()

            ip.nextPeriodBtn.setEnabled(False)
            ip.recalcPeriodBtn.setEnabled(False)
            ip.submitExpensesBtn.setEnabled(False)
            ip.submitIncomeBtn.setEnabled(False)
            ip.refreshOutputBtn.setEnabled(False)
            ip.changeScenarioBtn.setEnabled(False)
            ip.saveExitBtn.setEnabled(False)
            ip.clearDataBtn.setEnabled(False)
        else:
            # Полноценная загрузка
            self._init_after_period()

    def on_confirm_period(self):
        dt = self.view.input_panel.startDateEdit.date().toPyDate()
        self.model.set_period_start(dt)
        self._init_after_period()

        # Активируем всё после подтверждения
        ip = self.view.input_panel
        ip.submitExpensesBtn.setEnabled(True)
        ip.submitIncomeBtn.setEnabled(True)
        ip.nextPeriodBtn.setEnabled(True)
        ip.refreshOutputBtn.setEnabled(True)
        ip.changeScenarioBtn.setEnabled(True)
        ip.saveExitBtn.setEnabled(True)
        ip.clearDataBtn.setEnabled(True)

    def _init_after_period(self):
        months = self.model.get_active_months()
        labels = [m.strftime("%B %Y") for m in months]

        ip = self.view.input_panel
        ip.set_month_buttons_labels(labels)
        ip.enable_date_selection(False)
        ip.enable_month_buttons(True)

        first = months[0]
        self.current_exp_month = first
        self.current_inc_month = first
        ip.month_buttons[0].setChecked(True)

        self._load_inputs_for(first)

    def _load_inputs_for(self, month: date):
        ip = self.view.input_panel
        md = self.model.months.get(month)

        if not md:
            ip.clear_expense_inputs()
            ip.clear_income_inputs()
            return

        exp_vals = {e.category.value: e.amount for e in md.entries if e.direction == "expense"}
        inc_vals = {e.category.value: e.amount for e in md.entries if e.direction == "income"}

        ip.set_expense_values(exp_vals)
        ip.set_income_values(inc_vals)
        
    def get_current_inputs(self) -> dict:
        ip = self.view.input_panel

        expenses = {}
        for name, widget in zip(self.expense_categories, ip.get_expense_inputs()):
            text = widget.text().strip()
            try:
                expenses[name] = Decimal(text) if text else Decimal("0")
            except InvalidOperation:
                raise ValueError(f"Invalid expense value in '{name}': {text}")

        incomes = {}
        income_names = self.income_guaranteed_categories + self.income_expected_categories
        for name, widget in zip(income_names, ip.get_income_inputs()):
            text = widget.text().strip()
            try:
                incomes[name] = Decimal(text) if text else Decimal("0")
            except InvalidOperation:
                raise ValueError(f"Invalid income value in '{name}': {text}")

        return {"expenses": expenses, "incomes": incomes}

    def on_select_month(self, btn):
        ip = self.view.input_panel
        for b in ip.month_buttons:
            b.setChecked(False)
        btn.setChecked(True)

        idx = ip.month_buttons.index(btn)
        month = self.model.get_active_months()[idx]
        self.current_exp_month = month
        self.current_inc_month = month

        self._load_inputs_for(month)

    def on_submit_expenses(self):
        try:
            inputs = self.get_current_inputs()["expenses"]
        except ValueError as e:
            QMessageBox.warning(self.view, "Invalid Input", str(e))
            return

        for name, amount in inputs.items():
            entry = Entry(
                date=self.current_exp_month,
                category=Category(name),
                direction="expense",
                amount=amount,
                type="forecast"
            )
            self.model.upsert_entry(entry)

        self._load_inputs_for(self.current_exp_month)

    def on_submit_incomes(self):
        try:
            inputs = self.get_current_inputs()["incomes"]
        except ValueError as e:
            QMessageBox.warning(self.view, "Invalid Input", str(e))
            return

        for name, amount in inputs.items():
            entry = Entry(
                date=self.current_inc_month,
                category=Category(name),
                direction="income",
                amount=amount,
                type="forecast"
            )
            self.model.upsert_entry(entry)

        self._load_inputs_for(self.current_exp_month)
        
    # Period shift

    def on_prepare_period_shift(self):
        try:
            self.model.shift.prepare()
        except PeriodShiftError as e:
            QMessageBox.warning(self.view, "Cannot Prepare Shift", str(e))
            return

        QMessageBox.information(
            self.view,
            "Period Shift Required",
            "Please enter actual values for the first month of the current period,\n"
            "save them using the Submit buttons, then press Recalculate Period."
        )

        self._pending_shift = True
        self._enter_pre_shift_ui_mode()
        
    def _enter_pre_shift_ui_mode(self):
        ip = self.view.input_panel

        ip.enable_date_selection(False)
        ip.enable_month_buttons(False)
        ip.confirmMonthBtn.setEnabled(False)
        ip.nextPeriodBtn.setEnabled(False)
        ip.recalcPeriodBtn.setEnabled(True)

        ip.submitExpensesBtn.setEnabled(True)
        ip.submitIncomeBtn.setEnabled(True)

        ip.refreshOutputBtn.setEnabled(False)
        ip.changeScenarioBtn.setEnabled(False)
        ip.saveExitBtn.setEnabled(False)
        ip.clearDataBtn.setEnabled(False)

        ip.clear_month_buttons_selection()
        ip.month_buttons[0].setChecked(True)

        month = self.model.get_active_months()[0]
        self.current_exp_month = month
        self.current_inc_month = month
        self._load_inputs_for(month)

    def on_recalc_period(self):
        if not self._pending_shift:
            QMessageBox.warning(
                self.view,
                "Action Required",
                "Please press 'Move Period Forward' and enter actual values first."
            )
            return

        try:
            self.model.shift.apply_shift()
        except PeriodShiftError as e:
            QMessageBox.critical(self.view, "Shift Failed", str(e))
            return

        self._pending_shift = False
        self._refresh_ui_after_shift()
        
    def _refresh_ui_after_shift(self):
        months = self.model.get_active_months()
        labels = [m.strftime("%B %Y") for m in months]
        ip = self.view.input_panel

        ip.set_month_buttons_labels(labels)
        ip.clear_month_buttons_selection()
        ip.month_buttons[0].setChecked(True)

        self.current_exp_month = months[0]
        self.current_inc_month = months[0]
        self._load_inputs_for(months[0])

        first_month = self.model.period_start + relativedelta(months=self.model.window_offset)
        ip.start_label.setText(first_month.strftime("%B %Y"))

        ip.enable_month_buttons(True)
        ip.nextPeriodBtn.setEnabled(True)
        ip.recalcPeriodBtn.setEnabled(False)
        ip.submitExpensesBtn.setEnabled(True)
        ip.submitIncomeBtn.setEnabled(True)
        ip.refreshOutputBtn.setEnabled(True)
        ip.changeScenarioBtn.setEnabled(True)
        ip.saveExitBtn.setEnabled(True)
        ip.clearDataBtn.setEnabled(True)
        ip.enable_date_selection(False)

    def on_clear_data(self):
        ip = self.view.input_panel
        ip.clearDataBtn.blockSignals(True)

        try:
            ans = QMessageBox.question(
                self.view, "Confirm Erase",
                "Are you sure you want to erase all data and restart?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if ans != QMessageBox.Yes:
                return

            ans = QMessageBox.question(
                self.view, "Backup Data",
                "Save a backup before erasing?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            do_backup = (ans == QMessageBox.Yes)

            self.model.reset(backup=do_backup)
            self._reset_ui_after_clear()

            QMessageBox.information(self.view, "Done", "Data erased; choose new start month.")
        finally:
            ip.clearDataBtn.blockSignals(False)
            
    def _reset_ui_after_clear(self):
        ip = self.view.input_panel

        ip.clear_expense_inputs()
        ip.clear_income_inputs()

        ip.enable_date_selection(True)
        ip.enable_month_buttons(False)
        ip.clear_month_buttons_selection()
        ip.start_label.setText("Choose month")

    def refresh(self):
        self._refresh_entries_table()
        self._refresh_forecast_table()
        self._refresh_charts()
        
    #Панель прогнозов
    
    def on_change_scenario(self):
        label = self.view.input_panel.scenario_label
        current = label.text().lower().strip()
        scenarios = ["baseline", "optimistic", "pessimistic"]

        try:
            idx = scenarios.index(current)
            next_scenario = scenarios[(idx + 1) % len(scenarios)]
        except ValueError:
            next_scenario = "baseline"

        label.setText(next_scenario)
        self.refresh()

    def _refresh_entries_table(self):
        months = self.model.get_active_months()
        headers = ["Category"] + [m.strftime("%b %Y") for m in months]

        all_cats_data = {}

        for month in months:
            md = self.model.months.get(month)
            if not md:
                continue
            for e in md.entries:
                if e.type != "forecast":
                    continue
                cat = e.category.value
                all_cats_data.setdefault(cat, {}).setdefault(month, 0)
                all_cats_data[cat][month] += e.amount

        rows = []
        groups = [
            ("Expenses", DEFAULT_EXPENSE_CATEGORIES),
            ("Guaranteed Income", DEFAULT_INCOME_GUARANTEED_CATEGORIES),
            ("Expected Income", DEFAULT_INCOME_EXPECTED_CATEGORIES),
        ]

        for group_name, group_cats in groups:
            # Добавляем строку заголовка группы
            rows.append((group_name, None))  # None - признак заголовка

            for cat in group_cats:
                if cat in all_cats_data:
                    row = [cat]
                    for month in months:
                        val = all_cats_data[cat].get(month, "")
                        row.append(str(val))
                    rows.append(row)

        # Заполняем таблицу с учетом заголовков групп
        self.view.output_panel.entries_table.clear()
        self.view.output_panel.entries_table.setColumnCount(len(headers))
        self.view.output_panel.entries_table.setHorizontalHeaderLabels(headers)
        self.view.output_panel.entries_table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            if row[1] is None:
                # Строка-заголовок группы
                item = QTableWidgetItem(row[0])
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                brush = QBrush(QColor(220, 220, 220))  # светло-серый фон
                item.setBackground(brush)
                self.view.output_panel.entries_table.setSpan(i, 0, 1, len(headers))  # объединяем всю строку
                self.view.output_panel.entries_table.setItem(i, 0, item)
            else:
                # Обычная строка данных
                for j, val in enumerate(row):
                    item = QTableWidgetItem(val)
                    self.view.output_panel.entries_table.setItem(i, j, item)

        self.view.output_panel.entries_table.resizeColumnsToContents()

    def _refresh_forecast_table(self):
        scenario_name = self.view.input_panel.scenario_label.text().lower()
        if scenario_name not in ("baseline", "optimistic", "pessimistic"):
            return

        headers, net_row, close_row, runway_row = self.model.generate_forecast_metrics(scenario_name, months=3)

        if not headers:
            return

        rows = [
            ["Net Cash Flow"] + net_row,
            ["Closing Balance"] + close_row,
            ["Runway (months)"] + runway_row,
        ]

        headers = ["Metric"] + headers
        self.view.output_panel.set_forecast_data(headers, rows)

    def _refresh_charts(self):
        scenario_name = self.view.input_panel.scenario_label.text().lower()
        net_flows, runways = self.model.get_chart_data(scenario_name)

        if not net_flows:
            return

        self._plot_chart(
            self.view.output_panel.figure1,
            self.view.output_panel.canvas1,
            "Net Cash Flow",
            net_flows
        )

        self._plot_chart(
            self.view.output_panel.figure2,
            self.view.output_panel.canvas2,
            "Runway",
            runways
        )

    def _plot_chart(self, figure, canvas, title: str, data: list[tuple]):
        figure.clear()
        ax = figure.add_subplot(111)
        self._plot_series(ax, title, data)
        figure.tight_layout()
        canvas.draw()

    def _plot_series(self, ax, title: str, data: list[tuple]):
        x_all = list(range(len(data)))
        y_all = [val for _, _, val in data]

        actual_points = [(i, val) for i, (typ, _, val) in enumerate(data) if typ == "actual"]
        forecast_points = [(i, val) for i, (typ, _, val) in enumerate(data) if typ == "forecast"]

        actual_x, actual_y = zip(*actual_points) if actual_points else ([], [])
        forecast_x, forecast_y = zip(*forecast_points) if forecast_points else ([], [])

        ax.clear()
        ax.set_title(title)
        ax.grid(True)
        ax.set_xticks(x_all)

        if title == "Runway":
            ax.set_xticklabels([])
        else:
            ax.set_xticklabels([str(i + 1) for i in x_all], rotation=0, ha="center")
        ax.set_xlabel("Month")

        if actual_x:
            ax.plot(actual_x, actual_y, color="red", linestyle="-", marker="o")
        if forecast_x:
            ax.plot(forecast_x, forecast_y, color="blue", linestyle="--", marker="x")
        if actual_points and forecast_points:
            last_actual_x, last_actual_y = actual_points[-1]
            first_forecast_x, first_forecast_y = forecast_points[0]
            ax.plot([last_actual_x, first_forecast_x],
                    [last_actual_y, first_forecast_y],
                    color="red", linestyle=":", linewidth=2)