import subprocess
import psutil
import time
import datetime

def get_process_metrics(process):
    """ Fetch CPU and RAM usage of the specific process. """
    try:
        # Normalize CPU usage by the number of logical CPUs
        cpu_usage = process.cpu_percent(interval=1) / psutil.cpu_count(logical=True)
        memory_info = process.memory_info()
        ram_usage = memory_info.rss  # Resident Set Size memory usage in bytes (actual RAM usage)
        return cpu_usage, ram_usage
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0, 0

def record_usage(game_command):
    start_time = datetime.datetime.now()
    print(f"Start - {start_time}")

    # Start the game or application
    process = subprocess.Popen(game_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    game_process = psutil.Process(process.pid)

    # Initialize peak usage variables
    peak_cpu = 0
    peak_ram = 0

    # Monitor CPU and RAM usage every second
    while process.poll() is None:
        current_cpu, current_ram = get_process_metrics(game_process)

        # Update peak values if current readings are higher
        peak_cpu = max(peak_cpu, current_cpu)
        peak_ram = max(peak_ram, current_ram)

        time.sleep(1)  # Sleep to limit the frequency of measurements

    # Wait for the process to finish if it's done between checks
    process.wait()

    end_time = datetime.datetime.now()
    print(f"End - {end_time}")

    # Print peak usages
    print(f"Peak CPU Usage: {peak_cpu}% (normalized per core)")
    print(f"Peak RAM/RSS Usage: {peak_ram} bytes")  # Now explicitly labeled as RAM usage

if __name__ == "__main__":
    game_command = ['python3', 'main.py']  # Command to run your game or application
    record_usage(game_command)
