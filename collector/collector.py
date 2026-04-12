import psutil
import time

prev = psutil.net_io_counters()

while True:
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent

    curr = psutil.net_io_counters()
    network = (curr.bytes_sent + curr.bytes_recv) - (prev.bytes_sent + prev.bytes_recv)
    prev = curr

   
    network = network / 1000000

    print(f"CPU: {cpu}, Network: {network}, Memory: {memory}")

    with open("data/metrics.csv", "a") as f:
        f.write(f"{cpu},{network},{memory}\n")

    time.sleep(2)
