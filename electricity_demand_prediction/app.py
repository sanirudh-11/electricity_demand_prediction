from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from pathlib import Path

app = Flask(__name__)
DATA_PATH = Path(__file__).parent / "data" / "electricity_demand.csv"

def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["datetime"])
    return df.sort_values("datetime").reset_index(drop=True)

def add_features(df):
    out = df.copy()
    out["hour"] = out.datetime.dt.hour
    out["day_of_week"] = out.datetime.dt.dayofweek
    out["month"] = out.datetime.dt.month
    out["day"] = out.datetime.dt.day
    out["is_weekend"] = (out.day_of_week >= 5).astype(int)
    return out

def train_model(df):
    featured = add_features(df)
    features = ["temperature_c", "humidity", "hour", "day_of_week", "month", "day", "is_weekend"]
    # Chronological split keeps later observations out of training.
    split = int(len(featured) * 0.8)
    train, test = featured.iloc[:split], featured.iloc[split:]
    model = RandomForestRegressor(n_estimators=180, max_depth=14, min_samples_leaf=2,
                                  random_state=42, n_jobs=-1)
    model.fit(train[features], train["demand_mw"])
    pred = model.predict(test[features])
    metrics = {
        "mae": round(float(mean_absolute_error(test.demand_mw, pred)), 2),
        "rmse": round(float(np.sqrt(mean_squared_error(test.demand_mw, pred))), 2),
        "r2": round(float(r2_score(test.demand_mw, pred)), 3)
    }
    return model, features, metrics, test, pred

@app.route("/")
def home():
    df = load_data()
    model, features, metrics, test, pred = train_model(df)
    latest = df.iloc[-1]
    return render_template("index.html",
        metrics=metrics,
        latest_date=latest.datetime.strftime("%d %b %Y, %H:%M"),
        latest_demand=round(float(latest.demand_mw), 1),
        average=round(float(df.demand_mw.mean()), 1),
        peak=round(float(df.demand_mw.max()), 1),
        records=len(df))

@app.route("/api/overview")
def overview():
    df = load_data()
    daily = df.set_index("datetime").resample("D").demand_mw.mean().tail(30)
    hourly = df.groupby(df.datetime.dt.hour).demand_mw.mean()
    return jsonify({
        "daily_labels": [x.strftime("%d %b") for x in daily.index],
        "daily_values": [round(float(x), 1) for x in daily.values],
        "hour_labels": [f"{int(x):02d}:00" for x in hourly.index],
        "hour_values": [round(float(x), 1) for x in hourly.values],
        "recent_labels": [x.strftime("%d %b %H:%M") for x in df.datetime.tail(48)],
        "recent_values": [round(float(x), 1) for x in df.demand_mw.tail(48)]
    })

@app.route("/api/predict", methods=["POST"])
def predict():
    payload = request.get_json(force=True)
    try:
        dt = pd.to_datetime(payload["datetime"])
        temp = float(payload["temperature"])
        humidity = float(payload["humidity"])
        if not (-10 <= temp <= 55) or not (0 <= humidity <= 100):
            raise ValueError("Temperature or humidity is outside the allowed range.")
        row = pd.DataFrame([{
            "temperature_c": temp, "humidity": humidity,
            "hour": dt.hour, "day_of_week": dt.dayofweek, "month": dt.month,
            "day": dt.day, "is_weekend": int(dt.dayofweek >= 5)
        }])
        df = load_data()
        model, features, metrics, _, _ = train_model(df)
        value = float(model.predict(row[features])[0])
        return jsonify({"demand": round(value, 1), "unit": "MW",
                        "note": "Model estimate based on the included demonstration dataset."})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@app.route("/api/data")
def data():
    df = load_data().tail(100)
    return jsonify([{"datetime": r.datetime.strftime("%Y-%m-%d %H:%M"),
                     "demand_mw": round(float(r.demand_mw), 1),
                     "temperature_c": round(float(r.temperature_c), 1),
                     "humidity": int(r.humidity)} for r in df.itertuples()])

if __name__ == "__main__":
    app.run(debug=True)
