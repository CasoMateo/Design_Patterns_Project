import subprocess
import psutil
import time
import datetime
import pygame
print(pygame.__version__)

def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
    battery_status = battery.percent if battery else 'No battery'
    return cpu_usage, ram_usage, battery_status

def record_usage():
    start_cpu, start_ram, start_battery = get_system_metrics()
    print(f"Start - {datetime.datetime.now()}: CPU: {start_cpu}%, RAM: {start_ram}%, Battery: {start_battery}%")
    
    # Start the game or application
    process = subprocess.Popen(['python3', 'main.py'])
    process.wait()  # Wait for the game to finish

    end_cpu, end_ram, end_battery = get_system_metrics()
    print(f"End - {datetime.datetime.now()}: CPU: {end_cpu}%, RAM: {end_ram}%, Battery: {end_battery}%")

    # Calculate deltas
    delta_cpu = end_cpu - start_cpu
    delta_ram = end_ram - start_ram
    delta_battery = start_battery - end_battery if isinstance(start_battery, float) and isinstance(end_battery, float) else 'No battery info'
    print(f"Delta: CPU: {delta_cpu}%, RAM: {delta_ram}%, Battery: {delta_battery}%")

if __name__ == "__main__":
    record_usage()
