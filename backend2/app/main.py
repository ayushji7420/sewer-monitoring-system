from fastapi import FastAPI, HTTPException
from . import alerts, db
from .schemas import SensorPacket
from .classify import classify_status

app = FastAPI()

@app.post("/api/v1/sensor-data")
def ingest(packet: SensorPacket):
    status = classify_status(packet.water_level_mm, packet.pipe_diameter_mm)

    prev_status = db.get_last_status(packet.node_id)
    db.insert_reading(packet, status)

    if status in ("yellow", "red") and status != prev_status:
        event_type = "overflow" if packet.water_level_mm / packet.pipe_diameter_mm >= 0.45 else "underflow"
        db.insert_event(packet.node_id, event_type, status, packet.timestamp)
        alerts.notify(packet.node_id, event_type, status)

    return {"status": "ok", "classified": status}

@app.get("/api/v1/sewers")
def list_sewers():
    """Latest reading + status per node — dashboard map pulls this."""
    return db.get_latest_per_node()

@app.get("/api/v1/sewers/{node_id}/history")
def sewer_history(node_id: str, hours: int = 24):
    return db.get_history(node_id, hours)

@app.get("/api/v1/events")
def recent_events(limit: int = 50):
    return db.get_recent_events(limit)