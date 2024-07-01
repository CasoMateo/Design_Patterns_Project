import subprocess
import psutil
import time
import datetime
import pygame

def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
    battery_status = f"{battery.percent:.2f}" if battery else 'No battery'  # Report battery with two decimal places
    return cpu_usage, ram_usage, battery_status

def get_memory_usage():
    process = psutil.Process()  # Get the current process
    memory_info = process.memory_info()
    return memory_info.rss  # Return RSS memory usage in bytes

def record_usage():
    start_cpu, start_ram, start_battery = get_system_metrics()
    start_memory = get_memory_usage()
    print(f"Start - {datetime.datetime.now()}: CPU: {start_cpu}%, RAM: {start_ram}%, Battery: {start_battery}%, Memory: {start_memory} bytes")
    
    # Start the game or application
    process = subprocess.Popen(['python3', 'main.py'])
    process.wait()  # Wait for the game to finish

    end_cpu, end_ram, end_battery = get_system_metrics()
    end_memory = get_memory_usage()
    print(f"End - {datetime.datetime.now()}: CPU: {end_cpu}%, RAM: {end_ram}%, Battery: {end_battery}%, Memory: {end_memory} bytes")

    # Calculate deltas
    delta_cpu = end_cpu - start_cpu
    delta_ram = end_ram - start_ram
    delta_memory = end_memory - start_memory
    delta_battery = f"{float(start_battery) - float(end_battery):.2f}" if 'No battery' not in (start_battery, end_battery) else 'No battery info'
    print(f"Delta: CPU: {delta_cpu}%, RAM: {delta_ram}%, Battery: {delta_battery}%, Memory: {delta_memory} bytes")

    
if __name__ == "__main__":
    record_usage()

