import os
import subprocess
import time

import requests
from dotenv import load_dotenv

working_directory = os.getcwd()
add_to_env = os.path.join(working_directory, '.env')
load_dotenv(add_to_env)

API = os.getenv('API')


'''
Programattically enables the Zed Attack Proxy using specified API key. Is considered a blocking call because ZAP never terminates
'''
def start_zap_daemon() -> subprocess.Popen:
    # subprocess.run(args=['zap', '-daemon', '-config', f'api.key={API}'])
    daemon = subprocess.Popen(args=['zap', '-daemon', '-config', f'api.key={API}'])
    print(f"daemon started; pid={daemon.pid}")
    return daemon
# def enable_zap(site: str, base_path: str) -> None:
#     path = f'{base_path}/{site}/{site}'
#     subprocess.run(args=['zap', '-daemon', '-newsession', path, '-config', f'api.key={API}'])


'''
Sends the ZAP shutdown request using specified API key
'''
def shutdown_zap(daemon:subprocess.Popen) -> None:
    requests.get(f"http://localhost:8080/JSON/core/action/shutdown/?apikey={API}")
    daemon.wait()


'''
Creates a file pointing to the root certificate at the specified location
'''
def get_zap_cert(target_file='rootcert.crt') -> str:
    cert = requests.get(f'http://localhost:8080/OTHER/core/other/rootcert/?apikey={API}')
    print(f'Certificate Response: {cert.status_code}')
    certificate_text = cert.content.decode('utf-8')
    with open(target_file, mode='w') as target:
        target.write(certificate_text)
    return certificate_text


if __name__ == '__main__':
    daemon = start_zap_daemon()
    time.sleep(10)
    print(get_zap_cert())
    time.sleep(10)
    shutdown_zap(daemon)

