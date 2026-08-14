from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from datetime import datetime
import pickle
import numpy as np

app = FastAPI()

# Load memory model
with open("ml/model_memory.pkl", "rb") as f:
    memory_model = pickle.load(f)

# In-memory storage for now (will move to PostgreSQL later)
sensor_readings = []
server_metrics = []
predictions = []
scaling_events = []
alerts = []

# ─── Models ───────────────────────────────────────────────────────────────────

class SensorData(BaseModel):
    device_id: str
    timestamp: str
    temperature: float
    humidity: float
    co2: float
    pm25: float
    pm10: float
    tvoc: float
    co: float
    light: float
    motion: int
    occupancy: int

class ServerMetrics(BaseModel):
    timestamp: str
    cpu: float
    memory: float
    network_traffic: float

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "AI Autoscaling API is running"}

@app.post("/ingest")
def ingest(data: SensorData):
    sensor_readings.append(data.dict())
    return {"status": "received", "device_id": data.device_id}

@app.post("/metrics")
def receive_metrics(data: ServerMetrics):
    server_metrics.append(data.dict())

    # Predict memory
    predicted_memory = memory_model.predict([[data.cpu, data.network_traffic]])[0]
    predicted_memory = round(predicted_memory, 2)

    # Autoscaling decision
    scale_up = predicted_memory > 80 or data.cpu > 80
    scale_down = predicted_memory < 20 and data.cpu < 20

    # Store prediction
    prediction = {
        "timestamp": data.timestamp,
        "cpu": data.cpu,
        "memory": data.memory,
        "predicted_memory": predicted_memory,
        "scale_up": scale_up,
        "scale_down": scale_down
    }
    predictions.append(prediction)

    # Log scaling event
    if scale_up:
        event = {"timestamp": data.timestamp, "action": "scale_up", "reason": f"predicted_memory={predicted_memory}% cpu={data.cpu}%"}
        scaling_events.append(event)

    if scale_down:
        event = {"timestamp": data.timestamp, "action": "scale_down", "reason": f"predicted_memory={predicted_memory}% cpu={data.cpu}%"}
        scaling_events.append(event)

    # Anomaly detection alert
    if data.cpu > 90:
        alerts.append({"timestamp": data.timestamp, "type": "HIGH_CPU", "value": data.cpu})
    if data.memory > 90:
        alerts.append({"timestamp": data.timestamp, "type": "HIGH_MEMORY", "value": data.memory})

    return prediction

@app.get("/predictions")
def get_predictions():
    return {"predictions": predictions[-50:]}

@app.get("/scaling-events")
def get_scaling_events():
    return {"scaling_events": scaling_events}

@app.get("/alerts")
def get_alerts():
    return {"alerts": alerts}

@app.get("/sensor-readings")
def get_sensor_readings():
    return {"sensor_readings": sensor_readings[-50:]}

@app.get("/dashboard-data")
def get_dashboard_data():
    return {
        "latest_metrics": server_metrics[-1] if server_metrics else None,
        "latest_prediction": predictions[-1] if predictions else None,
        "total_scaling_events": len(scaling_events),
        "total_alerts": len(alerts),
        "total_sensor_readings": len(sensor_readings)
    }