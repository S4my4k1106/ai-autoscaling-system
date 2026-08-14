from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import pickle
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

with open("ml/model_memory.pkl", "rb") as f:
    memory_model = pickle.load(f)

sensor_readings = []
server_metrics = []
predictions = []
scaling_events = []
alerts = []

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

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

@app.get("/")
def root():
    return {"status": "AI Autoscaling API is running"}

@app.post("/ingest")
def ingest(data: SensorData):
    sensor_readings.append(data.dict())
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sensor_readings 
            (device_id, timestamp, temperature, humidity, co2, pm25, pm10, tvoc, co, light, motion, occupancy)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (data.device_id, data.timestamp, data.temperature, data.humidity,
              data.co2, data.pm25, data.pm10, data.tvoc, data.co, data.light,
              data.motion, data.occupancy))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB error: {e}")
    return {"status": "received", "device_id": data.device_id}

@app.post("/metrics")
async def receive_metrics(data: ServerMetrics):
    server_metrics.append(data.dict())

    predicted_memory = float(memory_model.predict([[data.cpu, data.network_traffic]])[0])
    predicted_memory = round(predicted_memory, 2)

    scale_up = bool(predicted_memory > 80 or data.cpu > 80)
    scale_down = bool(predicted_memory < 20 and data.cpu < 20)

    prediction = {
        "timestamp": data.timestamp,
        "cpu": data.cpu,
        "memory": data.memory,
        "predicted_memory": predicted_memory,
        "scale_up": scale_up,
        "scale_down": scale_down
    }
    predictions.append(prediction)

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO server_metrics (timestamp, cpu, memory, network_traffic)
            VALUES (%s, %s, %s, %s)
        """, (data.timestamp, data.cpu, data.memory, data.network_traffic))

        cur.execute("""
            INSERT INTO predictions (timestamp, cpu, memory, predicted_memory, scale_up, scale_down)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data.timestamp, data.cpu, data.memory, predicted_memory, scale_up, scale_down))

        if scale_up:
            cur.execute("""
                INSERT INTO scaling_events (timestamp, action, reason)
                VALUES (%s, %s, %s)
            """, (data.timestamp, "scale_up", f"predicted_memory={predicted_memory}%"))
            scaling_events.append({"timestamp": data.timestamp, "action": "scale_up", "reason": f"predicted_memory={predicted_memory}%"})

        if scale_down:
            cur.execute("""
                INSERT INTO scaling_events (timestamp, action, reason)
                VALUES (%s, %s, %s)
            """, (data.timestamp, "scale_down", f"predicted_memory={predicted_memory}%"))
            scaling_events.append({"timestamp": data.timestamp, "action": "scale_down", "reason": f"predicted_memory={predicted_memory}%"})

        if data.cpu > 90:
            cur.execute("""
                INSERT INTO alerts (timestamp, type, value)
                VALUES (%s, %s, %s)
            """, (data.timestamp, "HIGH_CPU", data.cpu))
            alerts.append({"timestamp": data.timestamp, "type": "HIGH_CPU", "value": data.cpu})

        if data.memory > 90:
            cur.execute("""
                INSERT INTO alerts (timestamp, type, value)
                VALUES (%s, %s, %s)
            """, (data.timestamp, "HIGH_MEMORY", data.memory))
            alerts.append({"timestamp": data.timestamp, "type": "HIGH_MEMORY", "value": data.memory})

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB error: {e}")

    await manager.broadcast(prediction)
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)