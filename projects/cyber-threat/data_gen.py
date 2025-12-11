# data_gen.py
import numpy as np
import pandas as pd
import os

os.makedirs("data", exist_ok=True)
N = 5000
rng = np.random.default_rng(42)

# features: duration, src_bytes, dst_bytes, src_packets, dst_packets, wrong_fragment, urgent, protocol (0=tcp,1=udp,2=icmp)
duration = np.abs(rng.normal(loc=1.0, scale=2.0, size=N))
src_bytes = np.abs(rng.normal(loc=300, scale=1000, size=N)).astype(int)
dst_bytes = np.abs(rng.normal(loc=200, scale=500, size=N)).astype(int)
src_packets = np.abs(rng.poisson(5, size=N))
dst_packets = np.abs(rng.poisson(3, size=N))
wrong_fragment = rng.integers(0,2,size=N)
urgent = rng.integers(0,2,size=N)
protocol = rng.choice([0,1,2], size=N, p=[0.7,0.25,0.05])

# generate label: 0 normal, 1 attack (make attacks rarer)
base_prob = 0.03 + (src_bytes > 1000)*0.05 + (duration>10)*0.05 + (protocol==2)*0.03
labels = (rng.random(N) < base_prob).astype(int)

df = pd.DataFrame({
    "duration": duration,
    "src_bytes": src_bytes,
    "dst_bytes": dst_bytes,
    "src_packets": src_packets,
    "dst_packets": dst_packets,
    "wrong_fragment": wrong_fragment,
    "urgent": urgent,
    "protocol": protocol,
    "label": labels
})

df.to_csv("data/synthetic_network.csv", index=False)
print("Wrote data/synthetic_network.csv, shape:", df.shape)
