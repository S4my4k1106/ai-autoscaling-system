import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
n = 50000

cpu = np.random.uniform(10, 95, n)
network = np.random.uniform(0, 100, n)
memory = (0.6 * cpu + 0.3 * network + np.random.normal(0, 5, n)).clip(0, 100)

timestamps = [datetime(2024, 1, 1) + timedelta(seconds=i) for i in range(n)]

df = pd.DataFrame({
    'timestamp': timestamps,
    'cpu': cpu.round(2),
    'memory': memory.round(2),
    'network_traffic': network.round(4)
})

df.to_csv("data/training_data.csv", index=False)
print(f"Done! {len(df)} rows generated")