import subprocess
import psutil
import time
import datetime
import pygame

def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=None)  # Get instant CPU usage
    ram_usage = psutil.virtual_memory().percent    # Get current RAM usage percentage
    battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
    battery_status = f"{battery.percent:.2f}" if battery else 'No battery'
    return cpu_usage, ram_usage, battery_status

def get_memory_usage():
    process = psutil.Process()  # Get the current process
    memory_info = process.memory_info()
    return memory_info.rss  # Return RSS memory usage in bytes

def record_usage():
    start_time = datetime.datetime.now()
    print(f"Start - {start_time}")

    # Initialize peak usage variables
    peak_cpu = 0
    peak_ram = 0
    peak_memory = 0

    # Start the game or application
    process = subprocess.Popen(['python3', 'main.py'])

    # Monitor CPU, RAM, and memory usage every second
    while process.poll() is None:
        current_cpu, current_ram, _ = get_system_metrics()
        current_memory = get_memory_usage()

        # Update peak values if current readings are higher
        peak_cpu = max(peak_cpu, current_cpu)
        peak_ram = max(peak_ram, current_ram)
        peak_memory = max(peak_memory, current_memory)

        time.sleep(1)  # Sleep to limit the frequency of measurements

    # Wait for the process to finish if it's done between checks
    process.wait()

    end_time = datetime.datetime.now()
    print(f"End - {end_time}")

    # Print peak usages
    print(f"Peak CPU Usage: {peak_cpu}%")
    print(f"Peak RAM Usage: {peak_ram}%")
    print(f"Peak Memory Usage: {peak_memory} bytes")

if __name__ == "__main__":
    record_usage()
