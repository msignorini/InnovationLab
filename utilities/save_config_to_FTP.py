import sys
sys.path.append('../')
import modules.arubaos_switch
import time
import os
import json
import ftplib
from pprint import pprint
from datetime import datetime, timezone
from configparser import ConfigParser


def upload_to_FTP(session, file_name):
    try:
        # file to send
        with open(file_name, 'rb') as file:
            print('Sending...')
            #session.cwd('Aruba') # /root/test
            # send the file
            session.storbinary('STOR {}'.format(file_name), file)
    except Exception as e:
        print(e)


def main():
    # directory containing the script
    path = os.path.dirname(os.path.abspath(__file__))
    # parent folder
    parent = os.path.dirname(os.path.abspath(path))
    # Configuration file parameters
    file = parent + '/config/params.cfg'
    config = ConfigParser()
    config.read(file)

    print("Connecting...")
    try:
        session = ftplib.FTPsession = ftplib.FTP(
            config.get('FTP', 'ftp_fqdn'),
            config.get('FTP', 'username'),
            config.get('FTP', 'password')
        )
        print('Session start...')
    except Exception as e:
        print(e)
        exit(1)

    # create switch objects
    switches = json.loads(config.get("Switches","switches"))
    for s in switches:
        s['obj'] = modules.arubaos_switch.ArubaOS_Switch(
            s['ip'], s['username'], s['password']
        )

        # switch login
        ret = s['obj'].login()
        if (ret['status'] != 0): # 0 means login ok
            msg = "Problem while login to switch, error: {}".format(
                ret['result']
            )
            print(msg)
            continue

        # show running config
        ret = s['obj'].show_running_config()
        # switch logout
        s['obj'].logout()
        if (ret['status'] != 0):
            msg = "Problem while retriving running config, \
                  error: {}".format(ret['result'])
            print(msg)
            continue

        file_name = s['ip']
        file_name += "_"
        file_name += datetime.fromtimestamp(
            time.time()
        ).strftime('%Y-%m-%d_%H-%M-%S')
        file_name += ".txt"

        with open(file_name, 'w') as file:
            file.write(ret['result'] + '\n')
        upload_to_FTP(session, file_name)
        #print(ret['result'])
        os.remove(file_name)

    print('Session quit...')
    session.quit()


if __name__ == '__main__':
    main()
