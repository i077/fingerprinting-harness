import subprocess
import requests
import os
from dotenv import load_dotenv

working_directory = os.getcwd()
add_to_env = os.path.join(working_directory, '.env')
load_dotenv(add_to_env)

API = os.getenv('API')

def enable_zap(site: str, base_path: str):
    path = f'{base_path}/{site}/{site}'
    subprocess.run(args=['zap', "-daemon", '-newsession', path, '-config', f'api.key={API}'])

def kill_zap():
    requests.get(f"http://localhost:8080/JSON/core/action/shutdown/?apikey={API}")

if __name__ == '__main__':
    enable_zap('cnn.com', '/home/zubair/zap/cnn2')