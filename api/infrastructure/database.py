import psycopg2
from dotenv import load_dotenv
import os

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def save_metrics(data):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO server_metrics (timestamp, cpu, memory, network_traffic)
            VALUES (%s, %s, %s, %s)
        """, (data.timestamp, data.cpu, data.memory, data.network_traffic))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB error: {e}")

def save_prediction(data, predicted_memory, predicted_cpu, scale_up, scale_down):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO predictions (timestamp, cpu, memory, predicted_memory, scale_up, scale_down)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data.timestamp, data.cpu, data.memory, predicted_memory, scale_up, scale_down))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB error: {e}")

def save_scaling_event(timestamp, action, reason):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO scaling_events (timestamp, action, reason)
            VALUES (%s, %s, %s)
        """, (timestamp, action, reason))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB error: {e}")

def save_alert(timestamp, alert_type, value):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO alerts (timestamp, type, value)
            VALUES (%s, %s, %s)
        """, (timestamp, alert_type, value))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB error: {e}")

def save_sensor_reading(data):
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