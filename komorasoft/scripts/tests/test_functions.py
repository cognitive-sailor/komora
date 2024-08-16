import psutil
import datetime as dt


def log_ram_usage():
    with open('log_ram.txt','a+') as f:
        message = f'RAM USAGE {dt.datetime.now()}: {psutil.virtual_memory().percent}%\n'
        f.write(message)

def log_cpu_usage():
    with open('log_cpu.txt','a+') as f:
        message = f'CPU USAGE {dt.datetime.now()}: {psutil.cpu_percent()}%\n'
        f.write(message)