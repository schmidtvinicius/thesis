import psutil
import time

def collect_hardware_metrics(cpu_percentage: list[int], bytes_written: list[int], write_times: list[int], stop_event):
    while not stop_event.is_set():
        cpu_percentage.append(psutil.cpu_percent(interval=None))
        disk_io_counters = psutil.disk_io_counters()
        bytes_written.append(disk_io_counters.write_bytes)
        write_times.append(disk_io_counters.write_time)
        time.sleep(1)
