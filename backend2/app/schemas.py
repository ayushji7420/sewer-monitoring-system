from pydantic import BaseModel, Field
from datetime import datetime

class SensorPacket(BaseModel):
    node_id: str
    timestamp: datetime
    water_level_mm: float = Field(ge=0)
    pipe_diameter_mm: float = Field(gt=0)
    tof_displacement_mm: float
    ir_blocked: bool
    battery_v: float
    rssi: int | None = None