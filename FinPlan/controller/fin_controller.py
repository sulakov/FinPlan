from datetime import date
from decimal import Decimal
from dateutil.relativedelta import relativedelta

from ..model.fin_model import FinModel
from ..model.entry import Entry
from ..model.category import Category
from ..model.period_shift import PeriodShiftError
from ..model.constants import (
    DEFAULT_EXPENSE_CATEGORIES,
    DEFAULT_INCOME_GUARANTEED_CATEGORIES,
    DEFAULT_INCOME_EXPECTED_CATEGORIES,
)
from .ui_controller import UIController


class FinController:
    """
    Main controller connecting UI events to data model logic:
    - Manages user interaction with period, entries, forecast and UI state
    """

    def __init__(self, view):
        """
        Initialize controller, model and hook up all signal handlers.
        """
        self.view = view
        self.model = FinModel()
        self.ui_controller = UIController(view)
        self._pending_shift = False  # becomes True after prepare() is called

        # Category lists used for input grid
        self.expense_categories = DEFAULT_EXPENSE_CATEGORIES
        self.income_categories = DEFAULT_INCOME_GUARANTEED_CATEGORIES + DEFAULT_INCOME_EXPECTED_CATEGORIES

        self.current_exp_month = None  # selected month for expenses
        self.current_inc_month = None  # selected month for incomes

        ip = view.input_panel

        # Connect control buttons to logic handlers
        ip.confirmMonthBtn.clicked.connect(self.on_confirm_period)
        ip.nextPeriodBtn.clicked.connect(self.on_prepare_period_shift)
        ip.recalcPeriodBtn.clicked.connect(self.on_recalc_period)
        ip.clearDataBtn.clicked.connect(self.on_clear_data)
        ip.refreshOutputBtn.clicked.connect(self.refresh)
        ip.changeScenarioBtn.clicked.connect(self.on_change_scenario)
        ip.saveExitBtn.clicked.connect(self.on_save_and_exit)

        ip.scenario_label.setText("baseline")  # initial scenario

        # Month selection buttons
        for btn in ip.month_buttons:
            btn.clicked.connect(lambda _, b=btn: self.on_select_month(b))

        # Submit actions
        ip.submitExpensesBtn.clicked.connect(self.on_submit_expenses)
        ip.submitIncomeBtn.clicked.connect(self.on_submit_incomes)

        # First-load: UI state depending on whether period already set
        if self.model.period_start is None:
            ip.enable_date_selection(True)
            ip.enable_month_buttons(False)
            ip.confirmMonthBtn.setEnabled(True)

            ip.nextPeriodBtn.setEnabled(False)
            ip.recalcPeriodBtn.setEnabled(False)
            ip.submitExpensesBtn.setEnabled(False)
            ip.submitIncomeBtn.setEnabled(False)
            ip.refreshOutputBtn.setEnabled(False)
            ip.changeScenarioBtn.setEnabled(False)
            ip.saveExitBtn.setEnabled(False)
            ip.clearDataBtn.setEnabled(False)
        else:
            self._init_after_period()

    def on_confirm_period(self):
        """Triggered when user clicks Confirm; saves start date and initializes UI"""
        dt = self.view.input_panel.startDateEdit.date().toPyDate()
        self.model.set_period_start(dt)
        self._init_after_period()
        self.ui_controller.enable_main_buttons()

    def _init_after_period(self):
        """Setup UI elements and load values for the selected month"""
        months = self.model.get_active_months()
        labels = [m.strftime("%B %Y") for m in months]
        self.ui_controller.init_after_period(labels, months[0])

        self.current_exp_month = months[0]
        self.current_inc_month = months[0]

        self._load_inputs_for(months[0])

    def _load_inputs_for(self, month: date):
        """Load input field values for a specific month from the model"""
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

    def get_current_inputs(self):
        """Reads user input from input fields and returns dict with decimals"""
        ip = self.view.input_panel

        expenses = {}
        for name, widget in zip(self.expense_categories, ip.get_expense_inputs()):
            text = widget.text().strip()
            expenses[name] = Decimal(text or "0")

        incomes = {}
        for name, widget in zip(self.income_categories, ip.get_income_inputs()):
            text = widget.text().strip()
            incomes[name] = Decimal(text or "0")

        return {"expenses": expenses, "incomes": incomes}

    def on_select_month(self, btn):
        """Triggered when user clicks on a quick month button"""
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
        """Submit expenses for current month as forecast entries"""
        inputs = self.get_current_inputs()["expenses"]
        month = self.current_exp_month or self.model.get_active_months()[0]

        for name, amount in inputs.items():
            entry = Entry(date=month, category=Category(name), direction="expense", amount=amount, type="forecast")
            self.model.upsert_entry(entry)

        self._load_inputs_for(month)

    def on_submit_incomes(self):
        """Submit incomes for current month as forecast entries"""
        inputs = self.get_current_inputs()["incomes"]
        month = self.current_inc_month or self.model.get_active_months()[0]

        for name, amount in inputs.items():
            entry = Entry(date=month, category=Category(name), direction="income", amount=amount, type="forecast")
            self.model.upsert_entry(entry)

        self._load_inputs_for(month)

    def on_prepare_period_shift(self):
        """Initiate shift process: ensure actual data for first month is ready"""
        try:
            self.model.shift.prepare()
        except PeriodShiftError as e:
            self.ui_controller.show_warning("Cannot Prepare Shift", str(e))
            return

        self.ui_controller.show_info(
            "Period Shift Required",
            "Please enter actual values for the first month of the current period,\n"
            "save them using the Submit buttons, then press Recalculate Period."
        )
        month = self.model.get_active_months()[0]
        self.ui_controller.enter_pre_shift_mode(month)
        self._pending_shift = True

    def on_recalc_period(self):
        """Apply period shift: forecasts -> actuals, move window"""
        if not self._pending_shift:
            self.ui_controller.show_warning(
                "Action Required",
                "Please press 'Move Period Forward' and enter actual values first."
            )
            return

        try:
            self.model.shift.apply_shift()
        except PeriodShiftError as e:
            self.ui_controller.show_warning("Shift Failed", str(e))
            return

        months = self.model.get_active_months()
        labels = [m.strftime("%B %Y") for m in months]
        first_month_label = (self.model.period_start + relativedelta(months=self.model.window_offset)).strftime("%B %Y")
        self.ui_controller.refresh_ui_after_shift(labels, months, first_month_label)
        self.current_exp_month = months[0]
        self.current_inc_month = months[0]
        self._load_inputs_for(months[0])

    def on_clear_data(self):
        """Erase all data with confirmation and optional backup"""
        if not self.ui_controller.confirm_dialog("Confirm Erase", "Are you sure you want to erase all data and restart?"):
            return

        backup = self.ui_controller.confirm_dialog("Backup Data", "Save a backup before erasing?")
        self.model.reset(backup)
        self.ui_controller.reset_ui_after_clear()
        self.current_exp_month = None
        self.current_inc_month = None

    def refresh(self):
        """Refresh entries table, forecast table, and charts"""
        self._refresh_entries_table()
        self._refresh_forecast_table()
        self._refresh_charts()

    def _refresh_entries_table(self):
        """Rebuild the forecast entries table"""
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
            rows.append((group_name, None))
            for cat in group_cats:
                if cat in all_cats_data:
                    row = [cat]
                    for month in months:
                        val = all_cats_data[cat].get(month, "")
                        row.append(str(val))
                    rows.append(row)

        self.ui_controller.refresh_entries_table(headers, rows)

    def _refresh_forecast_table(self):
        """Update forecast metrics table (cashflow, closing balance, runway)"""
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
        self.ui_controller.refresh_forecast_table(headers, rows)

    def _refresh_charts(self):
        """Refresh matplotlib charts for cashflow and runway"""
        scenario_name = self.view.input_panel.scenario_label.text().lower()
        net_flows, runways = self.model.get_chart_data(scenario_name)
        if not net_flows:
            return

        self.ui_controller.refresh_charts(net_flows, runways)

    def on_change_scenario(self):
        """Cycle through forecast scenarios"""
        ip = self.view.input_panel
        scenarios = ["baseline", "optimistic", "pessimistic"]
        current = ip.scenario_label.text().lower()
        next_scenario = scenarios[(scenarios.index(current) + 1) % len(scenarios)]
        ip.scenario_label.setText(next_scenario)
        self.refresh()

    def on_save_and_exit(self):
        """Save all data and close the app"""
        try:
            self.model.store.save(self.model.period_start, self.model.window_offset, self.model.months)
        except Exception as e:
            self.ui_controller.show_warning("Save Failed", f"Failed to save data: {e}")
            return
        self.view.close()