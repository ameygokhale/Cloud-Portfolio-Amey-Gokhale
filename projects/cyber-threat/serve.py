# serve.py
import joblib
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
import pandas as pd

app = FastAPI(title="Local Threat Detector")

MODEL_PATH = "models/model.joblib"
SCALER_PATH = "processed/scaler.joblib"
FEATURES_PATH = "processed/features.csv"

model = None
scaler = None
features = None

class Instance(BaseModel):
    # dynamic dictionary of features
    data: Dict[str, Any]

class Batch(BaseModel):
    instances: List[Instance]

@app.on_event("startup")
def load_artifacts():
    global model, scaler, features
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    features = pd.read_csv(FEATURES_PATH, header=None).iloc[:,0].tolist()
    print("Loaded model, scaler, features", len(features))

@app.post("/predict")
def predict(batch: Batch):
    # build dataframe from incoming instances
    rows = []
    for inst in batch.instances:
        rows.append(inst.data)
    X = pd.DataFrame(rows)
    # Ensure all required features present (missing fill 0)
    X = pd.get_dummies(X)
    # Add missing columns that were in training
    for c in features:
        if c not in X.columns:
            X[c] = 0
    # Keep only train features and in same order
    X = X[features]
    Xs = scaler.transform(X)
    preds = model.predict(Xs).tolist()
    probs = model.predict_proba(Xs)[:,1].tolist() if hasattr(model, "predict_proba") else None
    return {"predictions": preds, "probabilities": probs}

@app.get("/")
def readme():
    return {"message": "POST /predict with JSON {\"instances\": [{\"data\": {...}}] }"}
