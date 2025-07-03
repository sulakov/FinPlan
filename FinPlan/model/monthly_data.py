from datetime import date
from decimal import Decimal
from typing import List
from .entry import Entry

class MonthlyData:
    """
    Holds all financial entries for a single month and computes summary metrics.

    Attributes:
      month: start date of the month (first day)
      entries: list of Entry objects for this month
    """
    def __init__(self, month: date, entries: List[Entry] = None):
        """
        Initialize MonthlyData for a given month.

        :param month: date (first day of the month)
        :param entries: optional list of existing Entry objects
        """
        self.month = month                       # month start date
        self.entries = entries or []             # list of entries

    def add_entry(self, entry: Entry):
        """
        Add an entry to this month's data.

        :param entry: Entry object to add
        :raises ValueError: if entry.date does not match this month
        """
        if entry.date != self.month:
            raise ValueError("Entry date does not match MonthlyData month")
        self.entries.append(entry)              # add valid entry

    @property
    def total_income(self) -> Decimal:
        """Return sum of all income amounts for this month."""
        return sum(
            e.amount for e in self.entries if e.direction == "income"
        )

    @property
    def total_expenses(self) -> Decimal:
        """Return sum of all expense amounts for this month."""
        return sum(
            e.amount for e in self.entries if e.direction == "expense"
        )

    @property
    def net_cash_flow(self) -> Decimal:
        """Return net cash flow (income minus expenses) for this month."""
        return self.total_income - self.total_expenses