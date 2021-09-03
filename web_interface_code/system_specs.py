import psutil

def cpu_percent():
    return psutil.cpu_percent(1) 

def memory_percent():
    memory = psutil.virtual_memory()
    return memory.percent

def disk_percent():
    disk = psutil.disk_usage('/')
    return disk.percent

def cpu_temperature():
    return psutil.sensors_temperatures()["cpu_thermal"][0].current
