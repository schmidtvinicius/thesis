CREATE SEQUENCE IF NOT EXISTS experiments_id_sequence START 1;

CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY DEFAULT nextval('experiments_id_sequence'),
    lakehouse VARCHAR,
    client VARCHAR,
    events_produced INTEGER,
    duration_ns BIGINT,
    waiting_time BIGINT,
    flush_inlined_duration BIGINT
);

CREATE TABLE IF NOT EXISTS events(
    experiment_id INTEGER REFERENCES experiments(id),
    trip_id BIGINT,
    read_duration_ns BIGINT,
    write_duration_ns BIGINT,
    PRIMARY KEY (experiment_id, trip_id)
);

CREATE SEQUENCE IF NOT EXISTS hardware_metrics_id_sequence START 1;

CREATE TABLE IF NOT EXISTS hardware_metrics(
    id INTEGER PRIMARY KEY DEFAULT nextval('hardware_metrics_id_sequence'),
    experiment_id INTEGER REFERENCES experiments(id),
    cpu_percentage INTEGER,
    bytes_written BIGINT,
    write_time_ms BIGINT
);
