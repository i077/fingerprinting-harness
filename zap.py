import subprocess
import requests

def enable_zap(site: str, base_path: str) -> subprocess.Popen:
    path = f'{base_path}/{site}/{site}'
    res = subprocess.Popen(args=['zap.bat', "-daemon", '-newsession', path])
    return res

def kill_zap(process: subprocess.Popen):
    process.kill()

if __name__ == '__main__':
    proc = enable_zap('cnn.com')
    print(proc.pid)