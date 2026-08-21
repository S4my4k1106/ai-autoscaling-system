import pickle

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(BASE_DIR, "ml/model_memory.pkl"), "rb") as f:
    memory_model = pickle.load(f)

with open(os.path.join(BASE_DIR, "ml/model_cpu.pkl"), "rb") as f:
    cpu_model = pickle.load(f)

WINDOW = 5
cpu_window = []
def predict(cpu, network_traffic, actual_memory):
    # Memory prediction
    predicted_memory = float(memory_model.predict([[cpu, network_traffic]])[0])
    predicted_memory = round(predicted_memory, 2)

    # CPU sliding window prediction
    cpu_window.append(cpu)
    if len(cpu_window) > WINDOW:
        cpu_window.pop(0)

    if len(cpu_window) == WINDOW:
        predicted_cpu = float(cpu_model.predict([cpu_window])[0])
        predicted_cpu = round(predicted_cpu, 2)
    else:
        predicted_cpu = cpu

    # Hybrid scaling decisions
    scale_up = bool(predicted_memory > 80 or predicted_cpu > 80 or actual_memory > 90)
    scale_down = bool(predicted_memory < 20 and predicted_cpu < 20 and actual_memory < 50)

    return predicted_memory, predicted_cpu, scale_up, scale_down