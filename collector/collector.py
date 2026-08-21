import psutil
import time
import os
import requests
from datetime import datetime

filepath = "data/metrics.csv"

if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
    with open(filepath, "w") as f:
        f.write("timestamp,cpu,memory,network_traffic\n")

prev = psutil.net_io_counters()

print("Collecting data... Press Ctrl+C to stop.")

while True:
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    curr = psutil.net_io_counters()
    network = (curr.bytes_sent + curr.bytes_recv) - (prev.bytes_sent + prev.bytes_recv)
    prev = curr
    network = round(network / 1000000, 4)

    print(f"[{timestamp}] CPU: {cpu}% | Memory: {memory}% | Network: {network} MB")

    with open(filepath, "a") as f:
        f.write(f"{timestamp},{cpu},{memory},{network}\n")

    try:
       requests.post("http://13.232.238.60:8000/metrics", json={
            "timestamp": timestamp,
            "cpu": cpu,
            "memory": memory,
            "network_traffic": network
        })
    except:
        pass

    time.sleep(1)