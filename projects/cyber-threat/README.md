# Cybersecurity Threat Detection System (Local Deployment – macOS M3)

This project demonstrates an end-to-end **machine learning threat detection system** built and deployed locally.  
It includes data generation, preprocessing, XGBoost model training, FastAPI deployment, and prediction testing.

Screenshots are included **after every step** to show execution proof.

---

# 1. Project Overview

Intrusion Detection Systems (IDS) classify network activity as **normal** or **malicious**.  
This project builds an ML-based IDS using:

- Synthetic network data  
- XGBoost model  
- FastAPI serving  
- Local client prediction  

---
# 3. Theory

## 3.1 Intrusion Detection
Detects malicious patterns in network flows, packet counts, bytes, and traffic statistics.

## 3.2 Why ML?
- Automates detection  
- Learns attack signatures  
- Can generalize to unseen threats  

## 3.3 Why XGBoost?
- Works extremely well with tabular data  
- Robust to outliers  
- Produces probabilities (useful for threat scoring)

## 3.4 Why FastAPI?
- Very fast  
- Auto-generated documentation  
- Easy JSON APIs  

---

# 4. How the Code Works (Theory of Each File)

## **4.1 data_gen.py**
Generates a synthetic dataset resembling network activity.

## **4.2 preprocess.py**
- Removes missing values  
- One-hot encodes categorical features  
- Scales numeric features  
- Creates train/val/test splits  

## **4.3 train.py**
- Trains XGBoost  
- Prints evaluation metrics  
- Saves model  

## **4.4 serve.py**
Runs FastAPI → loads model → serves predictions at:

```
http://127.0.0.1:8000/predict
```

## **4.5 predict_client.py**
Sends POST requests to the API for testing.

## **4.6 run_pipeline.py**
Runs:
```
data_gen → preprocess → train
```

---

# 5. Step-by-Step Execution (with screenshots after each step)

---

## **STEP 1 — Open Terminal & Navigate to the Project Folder**
```bash
cd "/Users/ameygokhale/Documents/Cyber Security/Project/cyber-threat-local"
ls
```

### **SS2 — Terminal showing project folder**
![Screenshot2](screenshots/Screenshot2.png)

---

## **STEP 2 — Create a Virtual Environment**
```bash
python3 -m venv venv
```

---

## **STEP 3 — Activate Virtual Environment**
```bash
source venv/bin/activate
```

### **SS3 — (venv) visible in terminal**
![Screenshot3](screenshots/Screenshot3.png)

---

## **STEP 4 — Install Dependencies**
```bash
pip install -r requirements.txt
```

### **SS4 — Requirements installation shown**
![Screenshot4](screenshots/Screenshot4.png)

---

## **STEP 5 — Generate Synthetic Network Data**
```bash
python3 data_gen.py
```
Expected output:
```
Wrote data/synthetic_network.csv, shape: (5000, 9)
```

### **SS5 — Output of data_gen.py**
![Screenshot5](screenshots/Screenshot5.png)

---

## **STEP 6 — Preprocess the Data**
```bash
python3 preprocess.py --input data/synthetic_network.csv --outdir processed
```
Should output:
```
Saved processed artifacts to processed
```

### **SS6 — Output of preprocess.py**
![Screenshot6](screenshots/Screenshot6.png)

---

## **STEP 7 — Train the ML Model (XGBoost)**
```bash
python3 train.py --processed processed --outdir models
```

Outputs metrics:

- Accuracy  
- Precision  
- Recall  
- F1  
- ROC-AUC  
- Confusion matrix  

### **SS7 — Training output + metrics**
![Screenshot7](screenshots/Screenshot7.png)

---

## **STEP 8 — Start the FastAPI Server**
```bash
uvicorn serve:app --reload --port 8000
```

Should display:
```
Uvicorn running on http://127.0.0.1:8000
Loaded model, scaler, features
```

### **SS8 — FastAPI server running**
![Screenshot8](screenshots/Screenshot8.png)

---

## **STEP 9 — Open Swagger UI**
Go to:

```
http://127.0.0.1:8000/docs
```

### **SS9 — FastAPI docs loaded**
![Screenshot9](screenshots/Screenshot9.png)

---

## **STEP 10 — Test Prediction Using predict_client.py**
In a second terminal (venv active):

```bash
python3 predict_client.py
```

Output example:
```
Status: 200
{'predictions': [0, 0], 'probabilities': [0.01, 0.15]}
```

### **SS10 — Client prediction output**
![Screenshot10](screenshots/Screenshot10.png)

---

## **STEP 11 — Run Full Pipeline (Optional)**
```bash
python3 run_pipeline.py
```

Runs:
```
data_gen → preprocess → train
```

### **SS11 — run_pipeline.py output**
![Screenshot11](screenshots/Screenshot11.png)

---

# 6. Model Performance Interpretation

From your training output:

- High **accuracy (95%)**
- **0 precision / 0 recall**  
- All predictions are "normal", meaning dataset is **class-imbalanced**
---

# 🏁 7. Conclusion

You successfully built a **local cybersecurity threat detection system** that includes:

✔ Data generation  
✔ Preprocessing  
✔ Model training  
✔ REST API deployment  
✔ Prediction testing  
✔ Screenshots for documentation  

