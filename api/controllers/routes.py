from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from entities.models import SensorData, ServerMetrics
from use_cases.prediction import predict
from infrastructure.database import (
    save_metrics, save_prediction, save_scaling_event,
    save_alert, save_sensor_reading
)

router = APIRouter()

sensor_readings = []
server_metrics = []
predictions = []
scaling_events = []
alerts = []

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

@router.get("/")
def root():
    return {"status": "AI Autoscaling API is running"}

@router.post("/ingest")
def ingest(data: SensorData):
    sensor_readings.append(data.dict())
    save_sensor_reading(data)
    return {"status": "received", "device_id": data.device_id}

@router.post("/metrics")
async def receive_metrics(data: ServerMetrics):
    server_metrics.append(data.dict())
    save_metrics(data)

    predicted_memory, predicted_cpu, scale_up, scale_down = predict(data.cpu, data.network_traffic)

    prediction = {
        "timestamp": data.timestamp,
        "cpu": data.cpu,
        "memory": data.memory,
        "predicted_memory": predicted_memory,
        "predicted_cpu": predicted_cpu,
        "scale_up": scale_up,
        "scale_down": scale_down
    }
    predictions.append(prediction)
    save_prediction(data, predicted_memory, predicted_cpu, scale_up, scale_down)

    if scale_up:
        reason = f"predicted_memory={predicted_memory}% predicted_cpu={predicted_cpu}%"
        save_scaling_event(data.timestamp, "scale_up", reason)
        scaling_events.append({"timestamp": data.timestamp, "action": "scale_up", "reason": reason})

    if scale_down:
        reason = f"predicted_memory={predicted_memory}% predicted_cpu={predicted_cpu}%"
        save_scaling_event(data.timestamp, "scale_down", reason)
        scaling_events.append({"timestamp": data.timestamp, "action": "scale_down", "reason": reason})

    if data.cpu > 90:
        save_alert(data.timestamp, "HIGH_CPU", data.cpu)
        alerts.append({"timestamp": data.timestamp, "type": "HIGH_CPU", "value": data.cpu})

    if data.memory > 90:
        save_alert(data.timestamp, "HIGH_MEMORY", data.memory)
        alerts.append({"timestamp": data.timestamp, "type": "HIGH_MEMORY", "value": data.memory})

    await manager.broadcast(prediction)
    return prediction

@router.get("/predictions")
def get_predictions():
    return {"predictions": predictions[-50:]}

@router.get("/scaling-events")
def get_scaling_events():
    return {"scaling_events": scaling_events}

@router.get("/alerts")
def get_alerts():
    return {"alerts": alerts}

@router.get("/sensor-readings")
def get_sensor_readings():
    return {"sensor_readings": sensor_readings[-50:]}

@router.get("/dashboard-data")
def get_dashboard_data():
    return {
        "latest_metrics": server_metrics[-1] if server_metrics else None,
        "latest_prediction": predictions[-1] if predictions else None,
        "total_scaling_events": len(scaling_events),
        "total_alerts": len(alerts),
        "total_sensor_readings": len(sensor_readings)
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)