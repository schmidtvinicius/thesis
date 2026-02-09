import duckdb

def save_results(lakehouse: str,
                 client: str,
                 exp_duration_ns: int,
                 events_produced: int,
                 flush_inlined_duration: int|None,
                 waiting: int,
                 event_stats: list[tuple],
                 cpu_percentage: list[int],
                 bytes_written: list[int],
                 write_times: list[int]) -> None:
    with duckdb.connect("results/results.duckdb") as conn:
        conn.execute("""INSERT INTO experiments 
                        (lakehouse, client, events_produced, duration_ns, waiting_time, flush_inlined_duration)
                        VALUES (?,?,?,?,?,?);""", [lakehouse, client, events_produced, exp_duration_ns, waiting, flush_inlined_duration])
        exp_id = conn.execute("SELECT currval('experiments_id_sequence');").fetchall()[0][0]
        for trip_id, read_duration, write_duration in event_stats:
            conn.execute(f"INSERT INTO events (experiment_id, trip_id, read_duration_ns, write_duration_ns) VALUES ({exp_id},?,?,?);", [trip_id, read_duration, write_duration])
        for cpu, bites, time in zip(cpu_percentage, bytes_written, write_times):
            conn.execute(f"INSERT INTO hardware_metrics (experiment_id, cpu_percentage, bytes_written, write_time_ms) VALUES ({exp_id},?,?,?);", [cpu, bites, time])


def setup_results_db(sql_init_path: str, results_path: str) -> None:
    with duckdb.connect(results_path) as conn:
        with open(sql_init_path, "r") as f:
            conn.execute(f.read())
