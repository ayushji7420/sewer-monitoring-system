from sqlalchemy import create_engine, text
import os

import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

def get_last_status(node_id: str):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT status FROM readings WHERE node_id=:n ORDER BY ts DESC LIMIT 1"),
            {"n": node_id},
        ).fetchone()
        return row[0] if row else None

def insert_reading(packet, status: str):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO readings (node_id, ts, water_level_mm, tof_displacement_mm,
                                   ir_blocked, battery_v, rssi, status)
            VALUES (:node_id, :ts, :wl, :tof, :ir, :batt, :rssi, :status)
        """), {
            "node_id": packet.node_id, "ts": packet.timestamp,
            "wl": packet.water_level_mm, "tof": packet.tof_displacement_mm,
            "ir": packet.ir_blocked, "batt": packet.battery_v,
            "rssi": packet.rssi, "status": status,
        })

def insert_event(node_id: str, event_type: str, severity: str, ts):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO events (node_id, event_type, severity, ts)
            VALUES (:node_id, :event_type, :severity, :ts)
        """), {"node_id": node_id, "event_type": event_type, "severity": severity, "ts": ts})

def get_latest_per_node():
    # MySQL has no DISTINCT ON — use a correlated subquery on max(ts) per node instead.
    query = text("""
        SELECT n.node_id, n.name, n.latitude, n.longitude, n.pipe_diameter_mm,
               r.water_level_mm, r.ir_blocked, r.status, r.ts
        FROM nodes n
        JOIN readings r ON r.node_id = n.node_id
        JOIN (
            SELECT node_id, MAX(ts) AS max_ts
            FROM readings
            GROUP BY node_id
        ) latest ON r.node_id = latest.node_id AND r.ts = latest.max_ts
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
        return [dict(r) for r in rows]

def get_history(node_id: str, hours: int):
    query = text("""
        SELECT ts, water_level_mm, status FROM readings
        WHERE node_id = :n AND ts >= NOW() - INTERVAL :h HOUR
        ORDER BY ts ASC
    """)
    with engine.connect() as conn:
        rows = conn.execute(query, {"n": node_id, "h": hours}).mappings().all()
        return [dict(r) for r in rows]

def get_recent_events(limit: int):
    query = text("SELECT * FROM events ORDER BY ts DESC LIMIT :lim")
    with engine.connect() as conn:
        rows = conn.execute(query, {"lim": limit}).mappings().all()
        return [dict(r) for r in rows]