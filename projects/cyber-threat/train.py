# train.py
import joblib
import os
import argparse
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

def load_processed(path="processed"):
    X_train, y_train = joblib.load(os.path.join(path, "train.joblib"))
    X_val, y_val = joblib.load(os.path.join(path, "val.joblib"))
    X_test, y_test = joblib.load(os.path.join(path, "test.joblib"))
    return X_train, y_train, X_val, y_val, X_test, y_test

def train_and_save(X_train, y_train, X_val, y_val, outdir="models"):
    os.makedirs(outdir, exist_ok=True)
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="logloss",
        n_jobs=1,
        verbosity=0,
    )
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    joblib.dump(model, os.path.join(outdir, "model.joblib"))
    print("Saved model to", os.path.join(outdir, "model.joblib"))
    return model

def evaluate(model, X_test, y_test):
    preds = model.predict(X_test)
    proba = model.predict_proba(X_test)[:,1] if hasattr(model, "predict_proba") else None
    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    auc = roc_auc_score(y_test, proba) if proba is not None else None
    cm = confusion_matrix(y_test, preds)
    print("Accuracy:", acc)
    print("Precision:", prec)
    print("Recall:", rec)
    print("F1:", f1)
    if auc is not None:
        print("ROC AUC:", auc)
    print("Confusion matrix:\n", cm)
    return {"accuracy":acc, "precision":prec, "recall":rec, "f1":f1, "auc":auc, "cm":cm}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--processed", default="processed")
    p.add_argument("--outdir", default="models")
    args = p.parse_args()
    X_train, y_train, X_val, y_val, X_test, y_test = load_processed(args.processed)
    model = train_and_save(X_train, y_train, X_val, y_val, outdir=args.outdir)
    evaluate(model, X_test, y_test)
