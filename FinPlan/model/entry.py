from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal
from .category import Category

@dataclass
class Entry:
    """
    Represents a single financial record for a given month.

    Attributes:
      date: the first day of the relevant month
      category: category of the entry (income or expense)
      direction: "income" or "expense"
      amount: monetary value as Decimal
      type: "forecast" or "actual"
    """
    date: date               # month of the entry (first day)
    category: Category       # category enum
    direction: Literal["income", "expense"]  # indicates income or expense
    amount: Decimal          # amount value
    type: Literal["forecast", "actual"]      # entry type

    def to_dict(self) -> dict:
        """
        Convert the Entry to a JSON-serializable dict.

        :return: mapping of entry fields to primitive types
        """
        return {
            "date": self.date.isoformat(),        # ISO date string
            "category": self.category.value,      # category name
            "direction": self.direction,          # "income" or "expense"
            "amount": str(self.amount),           # decimal as string
            "type": self.type,                    # "forecast" or "actual"
        }