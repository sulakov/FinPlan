from enum import Enum

class Category(Enum):
    # Expenses
    EmployeeSalaries = "Employee Salaries"
    TaxesAndFees = "Taxes and Fees"
    RentAndUtilities = "Rent and Utilities"
    SubscriptionsAndITServices = "Subscriptions and IT Services"
    MarketingAdvertisingPromotion = "Marketing, Advertising, Promotion"
    FreelancersContractors = "Freelancers/Contractors"
    LoanInterests = "Loan Interests"
    LoanPrincipal = "Loan Principal"
    OtherExpenses = "Other Expenses"

    # Guaranteed Income
    SubscriptionsPaid = "Subscriptions (paid)"
    PrepaidContracts = "Prepaid Contracts"
    ConfirmedInvestments = "Confirmed Investments"

    # Expected Income
    PotentialSales = "Potential Sales"
    PlannedButUnconfirmedInvestments = "Planned but Unconfirmed Investments"
    CrowdfundingExpected = "Crowdfunding (expected)"