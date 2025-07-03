from datetime import date, datetime
from decimal import Decimal
import shutil
from pathlib import Path
from dateutil.relativedelta import relativedelta

from .monthly_data import MonthlyData
from .scenario import Scenario
from .data_store import DataStore
from .entry import Entry
from .period_shift import PeriodShift

class FinModel:
    """
    Core business logic managing a rolling three-month window of financial data.

    Attributes:
      WINDOW_LENGTH: number of months in the rolling window (3)
      store: DataStore instance for persistence
      period_start: date or None indicating start of period
      window_offset: int offset of the current window
      months: dict mapping month start date to MonthlyData
      active_months: list of dates in the current window
      shift: PeriodShift instance for window navigation
    """

    WINDOW_LENGTH = 3  # months in the window

    def __init__(self):
        """
        Initialize the model:
        - load saved data
        - compute active months list
        - set up period shifting helper
        """
        self.store = DataStore()  # persistence layer
        ps, wo, months = self.store.load()
        self.period_start = ps or None            # starting month of period
        self.window_offset = wo                   # window offset index
        self.months = months or {}                # all stored months
        self._recalc_window()                     # compute active_months
        self.shift = PeriodShift(self)            # navigation helper

    def _recalc_window(self):
        """
        Compute the list of active months based on period_start and window_offset.
        """
        if not self.period_start:
            self.active_months = []
        else:
            base = self.period_start + relativedelta(months=self.window_offset)
            self.active_months = [
                base + relativedelta(months=i)
                for i in range(self.WINDOW_LENGTH)
            ]

    def set_period_start(self, dt: date):
        """
        Set the starting month for the rolling window and reset offset.

        :param dt: any date within desired start month
        """
        self.period_start = dt.replace(day=1)
        self.window_offset = 0
        self._recalc_window()
        self.store.save(self.period_start, self.window_offset, self.months)

    def get_active_months(self) -> list[date]:
        """Return the list of dates in the current rolling window."""
        return self.active_months

    def add_entry(self, entry: Entry):
        """
        Append a new financial entry and persist changes.

        :param entry: Entry to add
        """
        md = self.months.setdefault(entry.date, MonthlyData(entry.date))
        md.add_entry(entry)
        self.store.save(self.period_start, self.window_offset, self.months)

    def upsert_entry(self, entry: Entry):
        """
        Insert or update an entry with matching date/category/direction/type.
        """
        md = self.months.setdefault(entry.date, MonthlyData(entry.date))
        replaced = False
        for idx, existing in enumerate(md.entries):
            if (
                existing.date == entry.date and
                existing.category == entry.category and
                existing.direction == entry.direction and
                existing.type == entry.type
            ):
                md.entries[idx] = entry
                replaced = True
                break

        if not replaced:
            md.add_entry(entry)

        self.store.save(self.period_start, self.window_offset, self.months)

    def generate_forecast(self, scenario_name: str) -> MonthlyData:
        """
        Create a forecast entry for the month following the most recent actual data.

        :param scenario_name: name of scenario to apply
        :returns: new MonthlyData for forecast month
        """
        if not self.months:
            raise ValueError("No data available to forecast")
        last_month = max(self.months)
        scenario = Scenario(scenario_name)
        forecast_md = scenario.apply(self.months[last_month])
        self.months[forecast_md.month] = forecast_md
        self.store.save(self.period_start, self.window_offset, self.months)
        return forecast_md

    def close_period(self):
        """
        Advance the rolling window by one month and persist state.
        """
        if not self.period_start:
            raise ValueError("Period start is not set")
        self.window_offset += 1
        self._recalc_window()
        self.store.save(self.period_start, self.window_offset, self.months)

    def get_overview(self) -> list[tuple[date, Decimal]]:
        """
        Return a list of tuples (month, net_cash_flow) for all stored months.
        """
        return [
            (m, md.net_cash_flow)
            for m, md in sorted(self.months.items())
        ]

    def generate_forecast_metrics(self, scenario_name: str, months: int = 3):
        """
        Compute forecast metrics (net cash flow, closing balance, runway)
        for each month in the active window based on a scenario.

        :param scenario_name: scenario key to apply
        :param months: number of months to include (default 3)
        :return: (headers, net_row, close_row, runway_row)
        """
        scenario = Scenario(scenario_name)
        forecast_months = []

        for m in self.get_active_months():
            md = self.months.get(m)
            if md:
                fm = scenario.apply(md, preserve_date=True)
                fm.month = m
                forecast_months.append(fm)

        if not forecast_months:
            return [], [], [], []

        # Determine actual months before the forecast window
        actual_months = [
            md for m, md in self.months.items()
            if m < forecast_months[0].month and any(e.type == "actual" for e in md.entries)
        ]
        initial_balance = sum(md.net_cash_flow for md in actual_months)

        # Weighted burn rate: 2x for actual, 1x for forecast
        weight_actual = 2
        weight_forecast = 1
        total_weight = len(actual_months)*weight_actual + len(forecast_months)*weight_forecast

        if total_weight:
            total_exp_actual = sum(md.total_expenses for md in actual_months)
            total_exp_forecast = sum(md.total_expenses for md in forecast_months)
            weighted_burn = (total_exp_actual*weight_actual + total_exp_forecast*weight_forecast) / total_weight
        else:
            weighted_burn = Decimal("1")

        headers = [md.month.strftime("%b %Y") for md in forecast_months]
        net_row, close_row, runway_row = [], [], []

        balance = initial_balance
        for fm in forecast_months:
            net = fm.net_cash_flow
            balance += net
            runway = (balance / weighted_burn) if weighted_burn else Decimal("0")
            net_row.append(str(net))
            close_row.append(str(balance))
            runway_row.append(str(round(runway, 2)))

        return headers, net_row, close_row, runway_row

    def get_chart_data(self, scenario_name: str):
        """
        Prepare data tuples for charting actual vs forecast flows and runways.

        :param scenario_name: scenario key
        :return: (net_flows, runways) lists of (type, label, value)
        """
        net_flows, runways = [], []

        hdrs, net_vals, _, runway_vals = self.generate_forecast_metrics(scenario_name)
        if not hdrs:
            return [], []

        # Plot actual data first
        balance = Decimal("0")
        for m in sorted(self.months):
            md = self.months[m]
            if any(e.type == "actual" for e in md.entries):
                net = md.net_cash_flow
                burn = (md.total_expenses / 3) if md.total_expenses else Decimal("1")
                run = (balance / burn) if burn else Decimal("0")
                net_flows.append(("actual", m.strftime("%b %Y"), float(net)))
                runways.append(("actual", m.strftime("%b %Y"), float(run)))
                balance += net

        # Then forecast values
        for lbl, net_str, rw_str in zip(hdrs, net_vals, runway_vals):
            nf = Decimal(net_str)
            rw = Decimal(rw_str)
            net_flows.append(("forecast", lbl, float(nf)))
            runways.append(("forecast", lbl, float(rw)))
            balance += nf

        return net_flows, runways

    def reset(self, backup: bool = True) -> None:
        """
        Clear all stored data, optionally backing up existing file first.

        :param backup: if True, copy old data.json to a timestamped backup
        """
        file_path = self.store.FILE
        if backup and file_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = file_path.with_name(f"data_backup_{timestamp}.json")
            shutil.copy(file_path, backup_file)

        # Reset in-memory state
        self.period_start = None
        self.window_offset = 0
        self.months = {}
        self._recalc_window()
        self.store.save(None, 0, {})