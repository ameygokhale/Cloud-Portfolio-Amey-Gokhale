# predict_client.py
import requests, json

url = "http://127.0.0.1:8000/predict"
payload = {
    "instances": [
        {"data": {"duration": 0.5, "src_bytes": 200, "dst_bytes": 50, "src_packets": 3, "dst_packets": 1, "wrong_fragment": 0, "urgent": 0, "protocol": 0}},
        {"data": {"duration": 50.0, "src_bytes": 5000, "dst_bytes": 4000, "src_packets": 200, "dst_packets": 180, "wrong_fragment": 1, "urgent": 0, "protocol": 1}}
    ]
}
r = requests.post(url, json=payload)
print("Status:", r.status_code)
print(r.json())
