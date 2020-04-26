import requests
import json
import base64
import requests
from pprint import pprint
import os
from configparser import ConfigParser
from time import sleep
import xml.etree.ElementTree as ET

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# return format
# {"status": <0, 1, 2>, "result": <something>}
# 0: ok
# 1: http error
# 2: exception
#'https://pa01.collabora.lab/api/?type=keygen&user=apiadmin&password=Sp4rk!01'

class PanOS():

    def __init__(self, fqdn, username, password):
        self.__username = username
        self.__password = password
        self.__url = "https://{}/api/".format(fqdn)

    def keygen(self):
        """ Obtain firewall key """

        params = {
    	    'type': 'keygen',
    	    'user': self.__username,
    	    'password': self.__password
        }

        try:
            response = requests.post(self.__url, data = params, verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code != 200):
            return {"status": 1, "result": response.status_code}

        root = ET.fromstring(response.text)
        if(root.get('status') == 'success'):
            self.__fwkey = root.find('./result/key').text
            #print(self.__fwkey)
            return {"status": 0, "result": response.text}


    def get_log_from_jobid(self, jobId):
        """ Obtain firewall key """
        #/api/?type=log&action=get&job-id=id
        params = {
            'type': 'log',
            'action': 'get',
            'job-id': jobId,
            'key': self.__fwkey
        }

        jobEnd = False
        while jobEnd == False:
            try:
                response = requests.post(self.__url, data = params, verify = False)
            except Exception as e:
                return {"status": 2, "result": str(e)}

            if (response.status_code != 200):
                return {"status": 1, "result": response.status_code}

            #print(response.text)
            root = ET.fromstring(response.text)
            if(root.get('status') == 'success'):
                #print('success')
                if(root.find('./result/job/status').text == 'FIN'):
                    jobEnd = True
                else:
                    print('Job {} not yet finished'.format(jobId))
                    sleep(2)

        return {"status": 0, "result": response.text}


    def get_threat_log(self):
        """ Obtain firewall key """
        #/api/?type=log&log-type=threat&nlogs=
        params = {
            'type': 'log',
            'log-type': 'threat',
            'nlogs': '5',
            'key': self.__fwkey
        }

        try:
            response = requests.post(self.__url, data = params, verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code != 200):
            return {"status": 1, "result": response.status_code}

        #print(response.text)
        root = ET.fromstring(response.text)
        if(root.get('status') == 'success'):
            #print('success')
            jobId = root.find('./result/job').text
            print('Job ID:', jobId)
            print('Wait 1 sec...')
            sleep(1)
            return self.get_log_from_jobid(jobId)


if __name__ == '__main__':
	print(__name__)
