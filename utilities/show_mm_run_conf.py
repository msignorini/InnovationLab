import sys
sys.path.append('../')
import modules.arubaos_controller
from pprint import pprint
from configparser import ConfigParser
import os
import json


def main():

    # directory containing the script
    path = os.path.dirname(os.path.abspath(__file__))
    # parent folder
    parent = os.path.dirname(os.path.abspath(path))
    # Configuration file parameters
    file = parent + '/config/params.cfg'
    config = ConfigParser()
    config.read(file)

    # create mobility master objects
    mobility_master = modules.arubaos_controller.ArubaOS_Controller(
        config.get('MobilityMaster', 'mm_fqdn'),
        config.get('MobilityMaster', 'username'),
        config.get('MobilityMaster', 'password')
    )

    # mobility master login
    ret = mobility_master.login()
    if (ret['status'] != 0): # 0 means login ok
        msg = "Problem while login to mobility master, \
              error: {}".format(ret['result'])
        print(msg)
        return

    ret = mobility_master.show_running_config()

    # mobility master logout
    mobility_master.logout()

    if (ret['status'] != 0):
        msg = "Problem while retreiving AP database, \
              error {}".format(ret['result'])
        print(msg)
        return

    pprint(ret['result'])


if __name__ == '__main__':
    main()
