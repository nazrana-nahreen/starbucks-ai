# =============================================================
# PHASE 2: FastAPI BACKEND (FIXED for actual column names)
# File: phase2_fastapi.py
# =============================================================
# HOW TO RUN:
#   python phase2_fastapi.py
#   Then open: http://localhost:8000/docs
# =============================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
import joblib
import numpy as np
import os
import uvicorn

print("Loading ML models...")

MODELS_DIR = "models"

def load_model(filename):
    path = os.path.join(MODELS_DIR, filename)
    if not os.path.exists(path):
        print(f"⚠️  Not found: {path} — run phase1_ml_models.py first!")
        return None
    return joblib.load(path)

spend_model      = load_model("spend_prediction_model.pkl")
wait_model       = load_model("wait_time_model.pkl")
kmeans_model     = load_model("kmeans_model.pkl")
label_encoders   = load_model("label_encoders.pkl")
cluster_scaler   = load_model("cluster_scaler.pkl")
spend_features   = load_model("spend_features.pkl")
wait_features    = load_model("wait_features.pkl")
cluster_features = load_model("cluster_features.pkl")
segment_names    = load_model("segment_names.pkl")

print("✅ Models loaded!")

app = FastAPI(
    title="☕ Starbucks AI Operations API",
    description="""
AI-powered predictions for Starbucks operations.

**Dataset facts:**
- 100,000 transactions | 500 stores | Jan 2024 – Dec 2025
- Mobile App users spend **45% more** ($18.08 vs $12.50)
- Drive-Thru is slowest channel (5.80 min avg wait)
- Peak hour: 7am

## Endpoints
- **/predict-spend** → Predict customer spend
- **/predict-wait-time** → Predict order wait time
- **/segment-customer** → Classify customer into persona
- **/insights** → Get key data insights
- **/health** → API status
    """,
    version="2.0.0"
)


# ── Data Models (using ConfigDict for Pydantic v2) ───────────

class SpendRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "order_channel": "Mobile App",
            "store_location_type": "Urban",
            "region": "Northeast",
            "customer_age_group": "25-34",
            "day_of_week": "Mon",
            "cart_size": 3,
            "num_customizations": 3,
            "is_rewards_member": True,
            "drink_category": "Espresso",
            "has_food_item": False,
            "order_ahead": True
        }
    })

    # Actual column names from the dataset
    order_channel: str          # "Mobile App" | "Drive-Thru" | "In-Store Cashier" | "Kiosk"
    store_location_type: str    # "Urban" | "Suburban" | "Rural"
    region: str                 # "Northeast" | "Southeast" | "Midwest" | "West" | "Southwest"
    customer_age_group: str     # "18-24" | "25-34" | "35-44" | "45-54" | "55+"
    day_of_week: str            # "Mon" | "Tue" | "Wed" | "Thu" | "Fri" | "Sat" | "Sun"
    cart_size: int              # 1-10  (was wrongly called num_items before)
    num_customizations: int     # 0-8
    is_rewards_member: bool     # True or False  (was wrongly called loyalty_member before)
    drink_category: str         # "Espresso"|"Frappuccino"|"Refresher"|"Tea"|"Brewed Coffee"|"Other"
    has_food_item: bool         # True or False
    order_ahead: bool           # True or False


class WaitTimeRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "order_channel": "Drive-Thru",
            "store_location_type": "Suburban",
            "region": "Midwest",
            "cart_size": 3,
            "num_customizations": 2,
            "day_of_week": "Mon",
            "order_ahead": False,
            "has_food_item": True
        }
    })

    order_channel: str
    store_location_type: str
    region: str
    cart_size: int
    num_customizations: int
    day_of_week: str
    order_ahead: bool
    has_food_item: bool


class SegmentRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "cart_size": 3,
            "num_customizations": 4,
            "total_spend": 18.50,
            "fulfillment_time_min": 5.2,
            "order_channel": "Mobile App",
            "is_rewards_member": True,
            "customer_satisfaction": 5,
            "has_food_item": False
        }
    })

    cart_size: int
    num_customizations: int
    total_spend: float
    fulfillment_time_min: float
    order_channel: str
    is_rewards_member: bool
    customer_satisfaction: int   # 1-5
    has_food_item: bool


# ── Helper: encode input into feature vector ─────────────────

def encode_features(data: dict, features: list) -> list:
    row = []
    for feature in features:
        if feature.endswith('_encoded'):
            original = feature.replace('_encoded', '')
            value = data.get(original)
            if value is None:
                row.append(0)
                continue
            # Boolean columns
            if isinstance(value, bool):
                row.append(int(value))
            # Text columns — use label encoder
            elif original in label_encoders:
                try:
                    encoded = label_encoders[original].transform([str(value)])[0]
                    row.append(int(encoded))
                except ValueError:
                    row.append(0)
            else:
                row.append(0)
        else:
            row.append(data.get(feature, 0))
    return row


# ── ENDPOINT: Health Check ────────────────────────────────────

@app.get("/health")
def health_check():
    return {
        "status": "✅ Running",
        "models": {
            "spend_model":  spend_model  is not None,
            "wait_model":   wait_model   is not None,
            "kmeans_model": kmeans_model is not None,
        }
    }


# ── ENDPOINT: Key Insights ────────────────────────────────────

@app.get("/insights")
def get_insights():
    """Returns pre-computed key insights from the 100K transaction dataset."""
    return {
        "dataset_summary": {
            "total_transactions": 100000,
            "unique_customers": 14988,
            "stores": 500,
            "date_range": "Jan 2024 – Dec 2025"
        },
        "channel_insights": {
            "avg_spend": {
                "Mobile App": 18.08,
                "In-Store Cashier": 12.51,
                "Kiosk": 12.49,
                "Drive-Thru": 12.48
            },
            "avg_wait_minutes": {
                "Drive-Thru": 5.80,
                "Mobile App": 4.51,
                "Kiosk": 4.01,
                "In-Store Cashier": 3.20
            },
            "avg_satisfaction": {
                "Mobile App": 3.86,
                "In-Store Cashier": 3.70,
                "Kiosk": 3.60,
                "Drive-Thru": 3.44
            }
        },
        "key_findings": [
            "Mobile App users spend 45% MORE than other channels ($18.08 vs ~$12.50)",
            "Drive-Thru is slowest (5.80 min) AND has lowest satisfaction (3.44/5)",
            "55+ age group has only 981 mobile orders vs 16,368 for 25-34",
            "Rewards members spend $1.63 more per visit on average",
            "Peak hour is 7am with 10,208 orders"
        ]
    }


# ── ENDPOINT: Predict Spend ───────────────────────────────────

@app.post("/predict-spend")
def predict_spend(request: SpendRequest):
    if spend_model is None:
        raise HTTPException(503, "Spend model not loaded. Run phase1_ml_models.py first.")

    data = request.model_dump()
    features = encode_features(data, spend_features)
    prediction = float(spend_model.predict([features])[0])

    # Compare to channel average
    channel_avgs = {
        "Mobile App": 18.08, "Drive-Thru": 12.48,
        "In-Store Cashier": 12.51, "Kiosk": 12.49
    }
    channel_avg = channel_avgs.get(data['order_channel'], 14.87)
    diff = prediction - channel_avg
    diff_label = f"${abs(diff):.2f} {'above' if diff > 0 else 'below'} channel average"

    return {
        "predicted_spend_usd": round(prediction, 2),
        "channel_average_usd": channel_avg,
        "vs_channel_average": diff_label,
        "insight": f"{data['order_channel']} order with {data['num_customizations']} customizations "
                   f"and cart size {data['cart_size']} → predicted ${prediction:.2f}"
    }


# ── ENDPOINT: Predict Wait Time ───────────────────────────────

@app.post("/predict-wait-time")
def predict_wait_time(request: WaitTimeRequest):
    if wait_model is None:
        raise HTTPException(503, "Wait model not loaded. Run phase1_ml_models.py first.")

    data = request.model_dump()
    features = encode_features(data, wait_features)
    prediction = float(wait_model.predict([features])[0])

    if prediction < 3.5:
        status = "🟢 Fast"
        advice = "Great speed! Customer experience should be positive."
    elif prediction < 5.0:
        status = "🟡 Normal"
        advice = "Average wait. Monitor during peak hours (7am, 12pm)."
    else:
        status = "🔴 Slow"
        advice = "⚠️ Above average wait. Consider adding staff or promoting mobile ordering."

    return {
        "predicted_wait_minutes": round(prediction, 1),
        "status": status,
        "operational_advice": advice,
        "note": f"Drive-Thru avg is 5.80 min | In-Store avg is 3.20 min"
    }


# ── ENDPOINT: Segment Customer ────────────────────────────────

@app.post("/segment-customer")
def segment_customer(request: SegmentRequest):
    if kmeans_model is None:
        raise HTTPException(503, "Clustering model not loaded. Run phase1_ml_models.py first.")

    data = request.model_dump()
    features = encode_features(data, cluster_features)
    features_scaled = cluster_scaler.transform([features])
    segment_id = int(kmeans_model.predict(features_scaled)[0])
    segment_label = segment_names.get(segment_id, f"Segment {segment_id}")

    recommendations = {
        0: "Offer loyalty rewards and exclusive early access to new seasonal drinks.",
        1: "Send 'We miss you' 20% discount coupons to increase visit frequency.",
        2: "Promote mobile-only menu items and in-app exclusive deals.",
        3: "Optimize drive-thru speed and offer value bundle deals."
    }

    return {
        "segment_id": segment_id,
        "segment_name": segment_label,
        "marketing_recommendation": recommendations.get(segment_id, "Standard engagement."),
        "profile_summary": {
            "spend": f"${data['total_spend']:.2f}",
            "cart_size": data['cart_size'],
            "customizations": data['num_customizations'],
            "channel": data['order_channel'],
            "rewards_member": data['is_rewards_member'],
            "satisfaction": f"{data['customer_satisfaction']}/5"
        }
    }


# ── START SERVER ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Starting Starbucks AI API Server...")
    print("=" * 60)
    print("\n📌 Open in browser: http://localhost:8000/docs")
    print("   Interactive docs — test every endpoint with buttons!\n")
    uvicorn.run("phase2_fastapi:app", host="0.0.0.0", port=8000, reload=False)
