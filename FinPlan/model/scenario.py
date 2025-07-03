from .monthly_data import MonthlyData
from .constants import SCENARIO_FACTORS
from .entry import Entry
from decimal import Decimal
from dateutil.relativedelta import relativedelta

class Scenario:
    """
    Applies scenario multipliers to a month's data to generate forecasts.

    Attributes:
      name: key identifying the scenario (e.g., 'optimistic', 'baseline', 'pessimistic')
      factors: dict with 'income' and 'expenses' Decimal multipliers
    """

    def __init__(self, name: str):
        """
        Initialize a Scenario with preset factors.

        :param name: scenario key, must exist in SCENARIO_FACTORS
        :raises ValueError: if scenario name is unknown
        """
        if name not in SCENARIO_FACTORS:
            raise ValueError(f"Unknown scenario: {name}")
        self.name = name                                  # store scenario name
        self.factors = SCENARIO_FACTORS[name]             # multiplier factors

    def apply(self, prev: MonthlyData, preserve_date: bool = False) -> MonthlyData:
        """
        Generate a forecast for the next month by multiplying each entry.

        :param prev: MonthlyData of the previous month
        :param preserve_date: if True, use prev.month for forecast month
        :return: new MonthlyData instance with forecast entries
        """
        # Determine forecast month
        if preserve_date:
            next_month = prev.month
        else:
            next_month = prev.month + relativedelta(months=1)

        forecast = MonthlyData(next_month)  # container for forecast entries
        for entry in prev.entries:
            # choose factor based on direction
            factor = (
                Decimal(self.factors['income'])
                if entry.direction == 'income'
                else Decimal(self.factors['expenses'])
            )  # Decimal multiplier
            adjusted_amount = entry.amount * factor  # scaled value

            # create new forecast entry
            forecast.entries.append(
                Entry(
                    date=next_month,
                    category=entry.category,
                    direction=entry.direction,
                    amount=adjusted_amount,
                    type="forecast"
                )
            )
        return forecast  # return populated forecast data