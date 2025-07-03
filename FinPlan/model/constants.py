# -*- coding: utf-8 -*-
"""
Application constants: scenario multipliers and default UI categories.
"""
from decimal import Decimal

# Forecast scenario multipliers for income and expenses
SCENARIO_FACTORS = {
    "optimistic":   {"income": Decimal("1.3"), "expenses": Decimal("0.8")},  # bullish case
    "baseline":     {"income": Decimal("1.0"), "expenses": Decimal("1.0")},  # expected case
    "pessimistic":  {"income": Decimal("0.7"), "expenses": Decimal("1.2")},  # conservative case
}

# Default expense categories shown in the UI
DEFAULT_EXPENSE_CATEGORIES = [
    "Employee Salaries",        # staff costs
    "Taxes and Fees",           # government charges
    "Rent and Utilities",       # office and services
    "Subscriptions and IT Services",  # software and tools
    "Marketing, Advertising, Promotion",  # outreach
    "Freelancers/Contractors",  # external help
    "Loan Interests",           # financing cost
    "Loan Principal",           # debt repayment
    "Other Expenses",           # miscellaneous
]

# Default guaranteed income categories
DEFAULT_INCOME_GUARANTEED_CATEGORIES = [
    "Subscriptions (paid)",         # recurring revenue
    "Prepaid Contracts",            # upfront payments
    "Confirmed Investments",        # committed funding
]

# Default expected income categories
DEFAULT_INCOME_EXPECTED_CATEGORIES = [
    "Potential Sales",              # projected sales
    "Planned but Unconfirmed Investments",  # pending funding
    "Crowdfunding (expected)",      # outreach campaigns
]