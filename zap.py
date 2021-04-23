import os
import subprocess
import time
from zapv2 import ZAPv2

import requests
from dotenv import load_dotenv

working_directory = os.getcwd()
add_to_env = os.path.join(working_directory, '.env')
load_dotenv(add_to_env)

API = os.getenv('API')
zed = ZAPv2(apikey=API)


def start_zap_daemon() -> subprocess.Popen:
    '''
    Programattically enables the Zed Attack Proxy using specified API key.
    Uses Popen and returns daemon process for use in process kill
    '''
    # subprocess.run(args=['zap', '-daemon', '-config', f'api.key={API}'])
    daemon = subprocess.Popen(args=['zap', '-daemon',
                                    '-config', f'api.key={API}'])
    print(f"daemon started; pid={daemon.pid}")
    return daemon


def shutdown_zap(daemon: subprocess.Popen) -> None:
    '''
    Sends the ZAP shutdown request using specified API key.
    Requires the Popen daemon process to end before returning.
    This should be run to make sure the entire system clears up.
    '''
    zed.core.shutdown(apikey=API)
    # requests.get(f"http://localhost:8080/JSON/core/action/shutdown/?apikey={API}")
    daemon.wait()


def get_zap_cert(target_file='zaproot.crt') -> str:
    '''
    Creates a file pointing to the root certificate at the specified location
    '''
    certificate_text = zed.core.rootcert(apikey=API)
    with open(target_file, mode='w') as target:
        target.write(certificate_text)
    return certificate_text


def make_new_zap_session(site: str):
    '''
    Creates a new Zap session in working directory/zap/<site>/<site>.session
    '''
    path = f'{os.getcwd()}/zap/{site}/{site}'
    zed.core.new_session(apikey=API, name=path)
    return


if __name__ == '__main__':
    daemon = start_zap_daemon()
    time.sleep(10)
    print(get_zap_cert())
    time.sleep(10)
    shutdown_zap(daemon)
