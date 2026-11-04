CREATE TABLE nodes (
    node_id          VARCHAR(20) PRIMARY KEY,
    name             VARCHAR(100) NOT NULL,
    latitude         DOUBLE NOT NULL,
    longitude        DOUBLE NOT NULL,
    pipe_diameter_mm FLOAT NOT NULL,
    zone             VARCHAR(50),
    installed_at     DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE readings (
    id                   BIGINT AUTO_INCREMENT PRIMARY KEY,
    node_id              VARCHAR(20) NOT NULL,
    ts                   DATETIME NOT NULL,
    water_level_mm       FLOAT,
    tof_displacement_mm  FLOAT,
    ir_blocked           BOOLEAN,
    battery_v            FLOAT,
    rssi                 INT,
    status               ENUM('green','yellow','red'),
    FOREIGN KEY (node_id) REFERENCES nodes(node_id),
    INDEX idx_readings_node_ts (node_id, ts DESC)
) ENGINE=InnoDB;

CREATE TABLE events (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    node_id     VARCHAR(20) NOT NULL,
    event_type  ENUM('overflow','underflow','blockage'),
    severity    ENUM('yellow','red'),
    ts          DATETIME NOT NULL,
    resolved_at DATETIME NULL,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
) ENGINE=InnoDB;