from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .fin_model import FinModel

class PeriodShiftError(Exception):
    """Raised when a period shift operation is invalid or fails."""
    pass

class PeriodShift:
    """
    Manages the rolling period window shifts:
    - prepare: mark readiness to shift
    - apply_shift: convert forecasts to actuals and advance the window
    """
    def __init__(self, model: 'FinModel'):
        """
        Initialize PeriodShift helper and auto-register with the model.

        :param model: FinModel instance to control
        """
        self.model = model
        self._pending = False               # flag indicating shift is prepared
        model.shift = self                  # auto-attach to FinModel

    def prepare(self) -> bool:
        """
        Mark that the next period shift is ready to apply.

        :return: True if the shift was prepared successfully
        :raises PeriodShiftError: if there are no active months
        """
        if not self.model.get_active_months():  # no data loaded
            raise PeriodShiftError("No months available for shift.")
        self._pending = True                  # ready to apply shift
        return True

    def apply_shift(self) -> None:
        """
        Execute the pending period shift:
        - convert all 'forecast' entries in the first active month to 'actual'
        - advance the rolling window in the model

        :raises PeriodShiftError: if prepare() was not called first
        """
        if not self._pending:
            raise PeriodShiftError(
                "Shift not prepared. Please call prepare() first."
            )

        first_month = self.model.get_active_months()[0]  # beginning of window
        md = self.model.months.get(first_month)
        if md:
            for entry in md.entries:
                if entry.type == "forecast":
                    entry.type = "actual"       # finalize forecast entries

        self.model.close_period()              # move window forward
        self._pending = False                  # reset readiness flag