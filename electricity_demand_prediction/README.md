# GridWise — Electricity Demand Prediction

A full-stack EVS mini-project website that explores electricity demand patterns and predicts demand using a Random Forest regression model.

## Features
- Dashboard with latest, average and peak demand indicators
- Daily trend and hourly consumption charts
- Interactive prediction form using date/time, temperature and humidity
- Recent observations table
- Flask backend and a scikit-learn Random Forest model
- Included CSV dataset (18 months of hourly **synthetic demonstration data**)

## Important dataset note
The included CSV is synthetic data generated for demonstrating the project workflow. It is **not official electricity-grid data** and must not be presented as actual CPCB, CEA, SLDC or utility readings. For a real-world submission, replace it with a verified dataset and retain the same column names:
`datetime,demand_mw,temperature_c,humidity`

## Run on Windows (PowerShell)
1. Extract the ZIP file.
2. Open the extracted `electricity_demand_prediction` folder in VS Code.
3. Open Terminal → PowerShell.
4. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
5. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run this once in that terminal:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```
6. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
7. Start the website:
   ```powershell
   python app.py
   ```
8. Open **http://127.0.0.1:5000** in your browser.

## How prediction works
The app extracts hour, day, weekday, month and weekend features from the requested timestamp. It trains a Random Forest Regressor using the first 80% of records in chronological order, tests on the last 20%, and returns an estimate for the entered weather conditions.

## Project structure
```text
electricity_demand_prediction/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── electricity_demand.csv
├── templates/
│   └── index.html
└── static/
    ├── app.js
    └── style.css
```

## Suggested project explanation
**Problem:** Electricity demand changes by time of day, day of week, season and weather. Poor estimation can make power generation and distribution planning harder.

**Solution:** GridWise displays historical demand patterns and uses a machine-learning regression model to estimate demand for a selected future date/time and weather conditions.

**Environmental relevance:** Better demand estimation can support more efficient generation scheduling, reduce avoidable reserve requirements and help integrate renewable energy. This prototype does not itself control electricity generation or prove emissions reductions.

## Limitations and future improvements
- Synthetic data is only for a functional demonstration.
- Replace the sample with real, documented regional data.
- Add holidays, real-time weather, renewable generation and more years of observations.
- Evaluate on a separate real-world test period and compare with baseline models.
