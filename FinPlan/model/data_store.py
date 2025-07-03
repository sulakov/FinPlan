import json
from pathlib import Path
from datetime import date
from decimal import Decimal
from .monthly_data import MonthlyData
from .entry import Entry
from .category import Category

class DataStore:
    """
    Handles loading and saving application data to a JSON file.

    Data format:
      {
        "meta": {"period_start": "YYYY-MM-DD" or null, "window_offset": int},
        "entries": {"YYYY-MM": [entry_dict, ...], ...}
      }

    Methods:
      - load(): returns (period_start, window_offset, months_dict)
      - save(period_start, window_offset, months_dict): writes JSON file
    """
    FILE = Path("data/data.json")

    def load(self):
        """
        Load stored data from disk.

        :returns: tuple(
            period_start: date or None,
            window_offset: int,
            months: dict[date, MonthlyData]
        )
        """
        if not self.FILE.exists():
            return None, 0, {}

        raw = json.loads(self.FILE.read_text())
        meta = raw.get("meta", {}) or {}

        # Extract metadata
        period_start = None
        if meta.get("period_start"):  # ISO date string
            period_start = date.fromisoformat(meta["period_start"])
        window_offset = int(meta.get("window_offset", 0))

        # Load entries organized by month
        months: dict[date, MonthlyData] = {}
        for m_str, entries in raw.get("entries", {}).items():
            # m_str format: YYYY-MM
            try:
                m_date = date.fromisoformat(f"{m_str}-01")
            except ValueError:
                continue  # skip invalid keys

            md = MonthlyData(m_date)
            for e in entries:
                entry = Entry(
                    date=date.fromisoformat(e["date"]),
                    category=Category(e["category"]),
                    direction=e["direction"],
                    amount=Decimal(e["amount"]),
                    type=e["type"]
                )
                md.entries.append(entry)
            months[m_date] = md

        return period_start, window_offset, months

    def save(self, period_start: date, window_offset: int, months: dict[date, MonthlyData]):
        """
        Persist metadata and monthly entries to the JSON file.

        :param period_start: starting date of the period or None
        :param window_offset: current window offset index
        :param months: mapping of month start date to MonthlyData
        """
        obj = {
            "meta": {
                "period_start": period_start.isoformat() if period_start else None,
                "window_offset": window_offset
            },
            "entries": {}
        }

        # Serialize each month's entries
        for m_date, md in months.items():
            key = m_date.strftime("%Y-%m")
            obj["entries"][key] = [e.to_dict() for e in md.entries]

        # Ensure directory exists and write file
        self.FILE.parent.mkdir(parents=True, exist_ok=True)
        self.FILE.write_text(json.dumps(obj, indent=2))