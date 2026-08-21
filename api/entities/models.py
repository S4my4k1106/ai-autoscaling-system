from pydantic import BaseModel

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

class Prediction(BaseModel):
    timestamp: str
    cpu: float
    memory: float
    predicted_memory: float
    predicted_cpu: float
    scale_up: bool
    scale_down: bool