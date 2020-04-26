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
        self.__credentials = 'username={}&password={}'.format(
            username,
            password
        )
        self.__api_endpoint  = "https://{}:4343/v1".format(ip)
        self.__UIDARUBA = None


    def login(self):
        """ Obtain cookie """

        headers = {
            'Content-Type': 'application/json'
        }

        url = self.__api_endpoint + '/api/login'

        try:
            response = requests.post(
                url,
                data = self.__credentials,
                headers = headers
        )
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200): # OK
            # convert JSON to dict
            dct = json.loads(response.text)
            self.__UIDARUBA = dct['_global_result']['UIDARUBA']
            return {"status": 0, "result": dct}

        # status_code != 200
        return {"status": 1, "result": response.status_code}


    def logout(self):
        """ Logout """

        headers = {
            'Content-Type': 'application/json'
        }

        cookie = {
            'SESSION': self.__UIDARUBA
        }

        url = self.__api_endpoint + '/api/logout'

        try:
            response = requests.get(url, cookies = cookie, headers = headers)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if response.status_code == 200: # OK
            # convert JSON to dict
            dct = json.loads(response.text)
            return {"status": 0, "result": dct}

        # status_code != 200
        return {"status": 1, "result": response.status_code}


    def api_get(self, url):
        """ Return the result of the get operation """

        """
        HTTP Status Code	Reason
        200                 Successful Response
        401                 Unauthorized
        403	                Forbidden
        415	                Unsupported Type
        """

        headers = {
            'Content-Type': 'application/json'
        }

        cookie = {
            'SESSION': self.__UIDARUBA
        }

        try:
            response = requests.get(url, cookies = cookie, headers = headers)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200): # OK
            dct = json.loads(response.text)
            return {"status": 0, "result": dct}

        # status_code != 200
        return {"status": 1, "result": response.status_code}


    def node_hierarchy(self):
        """ Get configuration node hierarchy of system """

        url = "{}/configuration/object/node_hierarchy?\
              json=1&UIDARUBA={}".format(
              self.__api_endpoint,
              self.__UIDARUBA
        )

        return self.api_get(url)


    def show_ap_database(self):
        """ Retrieve the access point database from Mobility Master """

        url = "{}/configuration/showcommand?\
              json=1&UIDARUBA={}&command={}".format(
              self.__api_endpoint,
              self.__UIDARUBA,
              'show ap database'
        )

        return self.api_get(url)


    def show_running_config(self):
        """ Retrieve the running configuration from Mobility Master """

        url = "{}/configuration/showcommand?\
              json=1&UIDARUBA={}&command={}".format(
              self.__api_endpoint,
              self.__UIDARUBA,
              'show running-config'
        )

        return self.api_get(url)
        

if __name__ == '__main__':
    print(__name__)
