import duckdb
import os

def save_results(lakehouse: str,
                 client: str,
                 exp_duration_ns: int,
                 events_produced: int,
                 flush_inlined_duration: int|None,
                 waiting: int,
                 event_stats: list[tuple],
                 cpu_percentage: list[int],
                 bytes_written: list[int],
                 write_times: list[int],
                 batch_write_size: int) -> None:
    with duckdb.connect(os.getenv("RESULTS_PATH")) as conn:
        conn.execute("BEGIN TRANSACTION;")
        conn.execute("""INSERT INTO experiments 
                        (lakehouse, client, events_produced, duration_ns, waiting_time, flush_inlined_duration)
                        VALUES (?,?,?,?,?,?);""", [lakehouse, client, events_produced, exp_duration_ns, waiting, flush_inlined_duration])
        exp_id = conn.execute("SELECT currval('experiments_id_sequence');").fetchall()[0][0]
        if batch_write_size == 1 or len(event_stats) % batch_write_size == 0:
            conn.execute("INSERT INTO events (experiment_id, trip_id, read_duration_ns, write_duration_ns) VALUES " + f"({exp_id},?,?,?),"*(len(event_stats)-1) + f"({exp_id},?,?,?);", [x for xs in event_stats for x in xs])
        else:
            conn.execute("INSERT INTO events (experiment_id, trip_id, read_duration_ns, write_duration_ns) VALUES " + f"({exp_id},?,?,?),"*(len(event_stats)-2) + f"({exp_id},?,?,?);", [x for xs in event_stats[:-1] for x in xs])
            last_event = event_stats[-1]
            conn.execute("UPDATE events SET write_duration_ns = ? WHERE trip_id = ? AND experiment_id = ?;", [last_event[-1], last_event[0], exp_id])
            # for trip_id, read_duration, write_duration in event_stats:
            #     if conn.execute("SELECT * FROM events WHERE trip_id = ? AND experiment_id = ?;", [trip_id, exp_id]).fetchone() is not None:
            #         conn.execute("UPDATE events SET write_duration_ns = ? WHERE trip_id = ? AND experiment_id = ?", [write_duration, trip_id, exp_id])
            #     else:
            #         conn.execute(f"INSERT INTO events (experiment_id, trip_id, read_duration_ns, write_duration_ns) VALUES ({exp_id},?,?,?);", [trip_id, read_duration, write_duration])
        for cpu, bites, time in zip(cpu_percentage, bytes_written, write_times):
            conn.execute(f"INSERT INTO hardware_metrics (experiment_id, cpu_percentage, bytes_written, write_time_ms) VALUES ({exp_id},?,?,?);", [cpu, bites, time])
        conn.execute("COMMIT;")


def setup_results_db(sql_init_path: str, results_path: str) -> None:
    with duckdb.connect(results_path) as conn:
        with open(sql_init_path, "r") as f:
            conn.execute(f.read())
