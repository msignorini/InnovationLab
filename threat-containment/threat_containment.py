import sys

# for direct use
sys.path.append('../')
# for Docker
sys.path.append('/app')

import modules.paloalto
import modules.telegram
import modules.aruba_clearpass
import datetime
import json
import xml.etree.ElementTree as ET
import os
from configparser import ConfigParser
from time import sleep
from pprint import pprint

# global object
cppm = None
firewall = None
telegram = None

def get_session_and_mac_from_ip(target_ip):
    ''' Get session_id associated to target_ip from ClearPass '''

    # check ClearPass token validity
    ret = cppm.check_token_validity()
    if (ret['status'] != 0):
        msg = "Problem with ClearPass token, error: {}".format(ret['result'])
        print(msg)
        return (None, None)

    # get current guest account list
    ret = cppm.get_session()
    if (ret['status'] != 0): # error
        msg = "Problem while retrieving ClearPass session, \
              error: {}".format(ret['result'])
        print(msg)
        return (None, None)

    #pprint(ret)
    for data in ret['result']['_embedded']['items']:
        if (data['state'] == 'active'):
            if (data['framedipaddress'] == target_ip):
                return (data['id'], data['mac_address'])

    # in case no session founds
    return (None, None)

def mark_compromised(mac_addr):
    # check ClearPass token validity
    ret = cppm.check_token_validity()
    if (ret['status'] != 0):
        msg = "Problem with ClearPass token, error: {}".format(ret['result'])
        print(msg)
        return ret['status']

    # get current guest account list
    ret = cppm.mark_compromised(mac_addr)
    if (ret['status'] != 0): # error
        msg = "Problem while marking the endpoint, \
              error: {}".format(ret['result'])
        print(msg)

    return ret['status']

def disconnect_session(session_id):
    # check ClearPass token validity
    ret = cppm.check_token_validity()
    if (ret['status'] != 0):
        msg = "Problem with ClearPass token, error: {}".format(ret['result'])
        print(msg)
        return ret['status']

    # get current guest account list
    ret = cppm.active_session_disconnect(session_id)
    if (ret['status'] != 0): # error
        msg = "Problem while disconnect the endpoint, \
              error: {}".format(ret['result'])
        print(msg)

    return ret['status']

def main():
    # reset timer
    new_offset = datetime.datetime.now()
    current_offset = new_offset

    # *****************************************************
    # directory containing the script
    path = os.path.dirname(os.path.abspath(__file__))
    # parent folder
    parent = os.path.dirname(os.path.abspath(path))

    # Configuration file parameters
    file = parent + '/config/params.cfg'
    config = ConfigParser()
    config.read(file)

    # create firewall object
    global firewall
    firewall = modules.paloalto.PanOS(
        config.get('Firewall', 'fw_fqdn'),
        config.get('Firewall', 'username'),
        config.get('Firewall', 'password')
    )

    # get firewall key
    ret = firewall.keygen()
    if(ret['status'] != 0):
        print(ret['result'])
        msg = "Error in retrieving Firewall key: {}".format(ret['result'])
        #logger.error(msg)
        print(msg)
        exit(1)

    # create ClearPass object
    global cppm
    cppm = modules.aruba_clearpass.ClearPass(
            config.get('ClearPass', 'clearpass_fqdn'),
            config.get('OAuth2', 'grant_type'),
            config.get('OAuth2', 'client_id'),
            config.get('OAuth2', 'client_secret'),
            config.get('OAuth2', 'username'),
            config.get('OAuth2', 'password')
    )

    # get ClearPass token
    ret = cppm.get_access_token()
    if (ret['status'] != 0):
        msg = "Error in creating ClearPass access \
              token: {}".format(ret['result'])
        #logger.error(msg)
        print(msg)
        exit(1)

    # create Telegram bot object
    global telegram
    telegram = modules.telegram.Telegram(
            config.get("Telegram","token"),
            json.loads(config.get("Telegram","whitelist"))
    )
    # *****************************************************

    try:
        while True:
            ret = firewall.get_threat_log()
            if(ret['status'] != 0):
                sleep(10)
                continue

            #print(ret['result'])
            root = ET.fromstring(ret['result'])
            #print(root.find('./result/log/logs/entry/src').text)
            print('[Threat Log]')
            compromized_addr = []
            for entry in root.findall('./result/log/logs/entry'):

                # check for new high severity threat log
                if(entry.find('severity').text == 'high'):

                    log_time = datetime.datetime.strptime(
                        entry.find('receive_time').text, '%Y/%m/%d %H:%M:%S'
                    )

                    print(entry.text)

                    # check if the newer log is newer than the offset
                    if (log_time > new_offset):
                        new_offset = log_time

                    #print('new offset:', new_offset)
                    #print('current offset:', current_offset)

                    # if the received log are older than the offset
                    # exit internal loop
                    if (log_time <= current_offset):
                        break

                    '''
                    print('|--------------------------------------|')
                    print('Severity:', entry.find('severity').text)
                    print('Receive Time:', entry.find('receive_time').text)
                    print('Source Address:', entry.find('src').text)
                    print('Destination Address:', entry.find('dst').text)
                    '''



                    msg = '|--------------------------------------|\n'
                    msg += 'Severity: {}\n'.format(entry.find('severity').text)
                    msg += 'Receive Time: {}\n'.format(entry.find('receive_time').text)
                    msg += 'Source Address: {}\n'.format(entry.find('src').text)
                    msg += 'Destination Address: {}\n'.format(entry.find('dst').text)

                    print(msg)
                    src_addr = entry.find('src').text
                    if src_addr not in compromized_addr:
                        compromized_addr.append(src_addr)
                    print("Lista ip compromessi:")
                    pprint(compromized_addr)
                    telegram.send_message('596368574', msg) # ID Telegram Marco


            for addr in compromized_addr:
                session_id, mac_addr = get_session_and_mac_from_ip(addr)
                if (session_id == None):
                    print('Unable to find session')
                    continue
                print('Session id: {}\nMac Address: {}'.format(session_id, mac_addr))
                ret = mark_compromised(mac_addr)
                if (ret != 0):
                    print('Unable to mark the endpoint')
                    continue
                ret = disconnect_session(session_id)


            current_offset = new_offset
            sleep(10)

    except KeyboardInterrupt:
        print('Application closed by user')
    print('\nBye!')

if __name__ == '__main__':
    main()
