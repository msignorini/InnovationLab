import sys
sys.path.append('../')
import modules.aruba_clearpass
import json
import os
from configparser import ConfigParser
from pprint import pprint

# directory containing the script
path = os.path.dirname(os.path.abspath(__file__))
# parent folder
parent = os.path.dirname(os.path.abspath(path))
# Configuration file parameters
file = parent + '/config/params.cfg'
config = ConfigParser()
config.read(file)

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

ret = cppm.get_session()
pprint(ret)
