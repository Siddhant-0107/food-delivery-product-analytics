from fastapi import FastAPI
from pydantic import BaseModel, Field
import pandas as pd
from src.models import load_model
from src.pricing import optimize_price

app = FastAPI(title='Food Delivery Intelligence API', version='1.0.0')

class OrderFeatures(BaseModel):
    distance_km: float = Field(gt=0, le=30)
    items: int = Field(ge=1, le=20)
    basket_value: float = Field(gt=0)
    hour: int = Field(ge=0, le=23)
    weekend: int = Field(ge=0, le=1)
    traffic: str
    weather: str

class PricingRequest(BaseModel):
    reference_price: float = Field(gt=0)
    base_demand: float = Field(gt=0)
    unit_cost: float = Field(gt=0)
    min_margin: float = Field(ge=0, lt=1, default=.20)


def frame(f: OrderFeatures):
    return pd.DataFrame([{
        'distance_km': f.distance_km, 'items': f.items, 'basket_value': f.basket_value,
        'hour': f.hour, 'weekend': f.weekend,
        'traffic': {'Low':0,'Medium':1,'High':2}[f.traffic],
        'weather': {'Clear':0,'Cloudy':1,'Rain':2}[f.weather]
    }])

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/predict/eta')
def predict_eta(features: OrderFeatures):
    model = load_model('eta_model.joblib')
    return {'eta_minutes': round(float(model.predict(frame(features))[0]), 2)}

@app.post('/predict/cancellation-risk')
def cancellation_risk(features: OrderFeatures):
    model = load_model('cancel_model.joblib')
    p = float(model.predict_proba(frame(features))[:,1][0])
    return {'cancellation_probability': round(p, 4)}

@app.post('/optimize/price')
def optimize(request: PricingRequest):
    result = optimize_price(request.reference_price, request.base_demand, request.unit_cost, request.min_margin)
    return {k: v for k, v in result.items() if k not in {'price_grid','revenue_grid'}}
