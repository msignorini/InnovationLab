import requests
import json
import base64
import requests
from pprint import pprint
import os
from configparser import ConfigParser
from time import sleep

# return format
# {"status": <0, 1, 2>, "result": <something>}
# 0: ok
# 1: http error
# 2: exception

class ArubaOS_Controller():

    def __init__(self, ip, username, password):
        self.credentials = 'username={}&password={}'.format(username, password)
        self.url = "https://{}:4343/v1/".format(ip)
        self.UIDARUBA = None

    def login(self):
        """ Obtain cookie """

        headers = {
            'Content-Type': 'application/json'
        }

        url = '{}api/login'.format(self.url)

        try:
            response = requests.post(url, data = self.credentials,
                                     headers = headers)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if response.status_code == 200: # login ok
            dct = json.loads(response.text)
            self.UIDARUBA = dct['_global_result']['UIDARUBA']
            return {"status": 0, "result": dct}

        return {"status": 1, "result": response.status_code}

    def logout(self):
        """ Logout from mobility controller """

        headers = {
            'Content-Type': 'application/json'
        }
        cookie = {
            'SESSION': self.UIDARUBA
        }

        url = '{}api/logout'.format(self.url)

        try:
            response = requests.get(url, cookies = cookie, headers = headers)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if response.status_code == 200: # logout ok
            dct = json.loads(response.text)
            return {"status": 0, "result": dct}

        return {"status": 1, "result": response.status_code}

    def node_hierarchy(self):

        headers = {
            'Content-Type': 'application/json'
        }
        cookie = {
            'SESSION': self.UIDARUBA
        }

        url = "{}configuration/object/node_hierarchy?\
              json=1&UIDARUBA={}".format(self.url, self.UIDARUBA)

        try:
            response = requests.get(url, cookies = cookie, headers = headers)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200): # ok
            dct = json.loads(response.text)
            return {"status": 0, "result": dct}

        return {"status": 1, "result": response.status_code}

    def ap_database(self):
        ''' Retrieve the access point database from Mobility Master '''

        headers = {
            'Content-Type': 'application/json'
        }
        cookie = {
            'SESSION': self.UIDARUBA
        }

        url = "{}configuration/showcommand?\
              json=1&UIDARUBA={}&command={}".format(
              self.url, self.UIDARUBA, 'show ap database')

        try:
            response = requests.get(url, cookies = cookie, headers = headers)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200): # ok
            dct = json.loads(response.text)
            return {"status": 0, "result": dct}

        return {"status": 1, "result": response.status_code}


if __name__ == '__main__':
    print(__name__)
