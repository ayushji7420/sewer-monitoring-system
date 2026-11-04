CREATE DATABASE IF NOT EXISTS sewer_monitoring
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE sewer_monitoring;


CREATE TABLE IF NOT EXISTS assets (
    id INT AUTO_INCREMENT PRIMARY KEY,

    asset_code VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,

    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,

    location_description TEXT,

    warning_level_cm DOUBLE NOT NULL DEFAULT 60.0,
    critical_level_cm DOUBLE NOT NULL DEFAULT 80.0,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_warning_level
        CHECK (warning_level_cm >= 0),

    CONSTRAINT valid_critical_level
        CHECK (critical_level_cm > warning_level_cm),

    CONSTRAINT valid_latitude
        CHECK (latitude BETWEEN -90 AND 90),

    CONSTRAINT valid_longitude
        CHECK (longitude BETWEEN -180 AND 180)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS readings (
    id INT AUTO_INCREMENT PRIMARY KEY,

    asset_id INT NOT NULL,

    level_cm DOUBLE NOT NULL,
    blocked BOOLEAN NOT NULL DEFAULT FALSE,
    cover_open BOOLEAN NOT NULL DEFAULT FALSE,

    battery_voltage DOUBLE,
    rssi INT,
    temperature_c DOUBLE,

    received_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sensor_timestamp DATETIME NULL,

    CONSTRAINT fk_readings_asset
        FOREIGN KEY (asset_id)
        REFERENCES assets(id)
        ON DELETE CASCADE,

    CONSTRAINT valid_level
        CHECK (level_cm >= 0),

    CONSTRAINT valid_battery_voltage
        CHECK (
            battery_voltage IS NULL
            OR battery_voltage >= 0
        )
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS alert_events (
    id INT AUTO_INCREMENT PRIMARY KEY,

    asset_id INT NOT NULL,
    reading_id INT NULL,

    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,

    sent_to_slack BOOLEAN NOT NULL DEFAULT FALSE,
    sent_to_email BOOLEAN NOT NULL DEFAULT FALSE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_alert_asset
        FOREIGN KEY (asset_id)
        REFERENCES assets(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_alert_reading
        FOREIGN KEY (reading_id)
        REFERENCES readings(id)
        ON DELETE SET NULL,

    CONSTRAINT valid_alert_severity
        CHECK (severity IN ('yellow', 'red'))
) ENGINE=InnoDB;


CREATE INDEX idx_readings_asset_received_at
    ON readings(asset_id, received_at);


CREATE INDEX idx_alert_events_created_at
    ON alert_events(created_at);