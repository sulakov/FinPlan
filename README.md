# FinPlan

**Version:** 0.1.0  
**Author:** Eugen Sulakov  

My first Python application in which I combined my previous experience as a finance professional with my modest programming skills. The idea originated as a simple Excel spreadsheet created to help a promising startup with short-term financial planning. Over time it evolved into a desktop GUI tool that lets you:

- Enter and categorize financial transactions (income, expenses, transfers)  
- Build scenarios and compare “what-if” projections side by side  
- Shift periods forward to simulate cash-flow timing changes  
- View aggregated monthly data in tables and charts  
- Generate interactive charts (via Matplotlib) for quick visual analysis  
- Save and load your workbook as JSON for easy sharing and backup  
- Customize categories and constants to fit your own business logic  

---
This is the very first version of the program; the code still needs refactoring and testing.

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
