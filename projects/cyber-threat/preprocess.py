# preprocess.py
import pandas as pd
import numpy as np
import joblib
import os
import argparse
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def load_data(path):
    df = pd.read_csv(path)
    return df

def preprocess(df):
    # Drop rows with NA
    df = df.dropna().reset_index(drop=True)
    # Assume 'label' column exists (0 normal, 1 attack). If not, raise.
    if 'label' not in df.columns:
        raise ValueError("Input CSV must contain a 'label' column.")
    X = df.drop(columns=['label'])
    y = df['label'].astype(int)
    # One-hot or keep numeric features: check dtypes
    # We'll one-hot any categorical column (object or int with few unique values)
    cat_cols = [c for c in X.columns if X[c].nunique() < 10 and X[c].dtype in ['int64','object']]
    X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
    return X, y

def split_and_scale(X, y, outdir="processed", test_size=0.2, val_size=0.1, random_state=42):
    os.makedirs(outdir, exist_ok=True)
    X_train, X_tmp, y_train, y_tmp = train_test_split(X, y, test_size=test_size+val_size, stratify=y, random_state=random_state)
    # split tmp into test & val proportionally
    val_ratio = val_size / (test_size + val_size)
    X_val, X_test, y_val, y_test = train_test_split(X_tmp, y_tmp, test_size=1-val_ratio, stratify=y_tmp, random_state=random_state)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)
    joblib.dump(scaler, os.path.join(outdir, "scaler.joblib"))
    # Save arrays
    joblib.dump((X_train_s, y_train), os.path.join(outdir, "train.joblib"))
    joblib.dump((X_val_s, y_val), os.path.join(outdir, "val.joblib"))
    joblib.dump((X_test_s, y_test), os.path.join(outdir, "test.joblib"))
    # Save feature list for serving
    pd.Series(X.columns).to_csv(os.path.join(outdir, "features.csv"), index=False, header=False)
    print("Saved processed artifacts to", outdir)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/synthetic_network.csv")
    p.add_argument("--outdir", default="processed")
    args = p.parse_args()
    df = load_data(args.input)
    X, y = preprocess(df)
    split_and_scale(X, y, outdir=args.outdir)
