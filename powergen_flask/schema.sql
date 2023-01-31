DROP TABLE IF EXISTS inputs;

CREATE TABLE inputs (
    network_voltage REAL NOT NULL,
    pole_cost REAL NOT NULL,
    pole_spacing REAL NOT NULL,
    resistance_per_km REAL NOT NULL,
    current_rating REAL NOT NULL,
    cost_per_km REAL NOT NULL,
    max_voltage_drop REAL NOT NULL);