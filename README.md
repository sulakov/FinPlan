# FinPlan

**Version:** 0.1.0  
**Author:** Eugen Sulakov  
This pet project was my way to learn Python by building something practical from scratch.
I used to work in finance, so I decided to recreate a planning tool I once had in Excel — but this time as a real desktop app.

Along the way I figured out how to structure the code with MVC, how to build a UI with PyQt5, and how to show charts using Matplotlib.
I also learned how to save and load data with JSON, and how to implement scenario-based forecasting logic.
It’s far from perfect, but it taught me a lot more than any tutorial.

It started out as a simple spreadsheet for short-term planning, but it's now a desktop GUI tool that lets you:

- Enter and categorize financial transactions (income, expenses, transfers)  
- Build and compare financial scenarios (“what-if” planning)  
- Shift periods forward to simulate cash-flow timing  
- View monthly data in tables and visual charts  
- Generate interactive charts using Matplotlib  
- Save and load your workbook as JSON (for sharing or backup)  
- Customize categories and constants to match your business logic  

---

This is the first version of the application. The code still requires refactoring and more testing.

![App screenshot](screenshot.jpg)


## Key technical and financial enhancements planned:

- Codebase refactoring and structure optimization  
- Adding unit tests and basic CI integration  
- Support for multiple workspaces (save/load separate sessions)  
- Secure login and encrypted file storage  
- Importing financial data from Excel files  
- Option to extend or shorten the forecast horizon (currently fixed to 3 months)
  
**Planned financial features:**
- Goal-based planning (e.g. “stay solvent until product launch”)  
- Side-by-side comparison of financial scenarios  
- Support for recurring vs. one-time income and expenses  
- Currency selection and exchange rate adjustments  
- Automatic data validation and balance checks (e.g., negative cash flows or incomplete entries


## Prerequisites

- Python 3.7 or higher  
- Windows, macOS or Linux  

---


## Project Structure

```
PROJECT_ROOT/
│
├── data/                  ← default JSON data storage
│   └── data.json
│
├── FinPlan/               ← main application package
│   ├── __init__.py
│   ├── __main__.py        ← application entry point
│   ├── controller/        ← business logic controllers
│   ├── model/             ← data models, scenarios, constants
│   ├── resources/         ← stylesheets, assets
│   └── view/              ← PyQt5 UI components
│
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
