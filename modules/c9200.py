import requests
import json
import base64
import requests
from pprint import pprint
import os
from configparser import ConfigParser
from time import sleep
from requests.auth import HTTPBasicAuth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# return format
# {"status": <0, 1, 2>, "result": <something>}
# 0: ok
# 1: http error
# 2: exception

class C9200():

    def __init__(self, ip, username, password):

        self.auth = HTTPBasicAuth(username, password)
        self.url = "https://{}:443".format(ip)


    def get_API(self, url):

        headers = {
            'Accept': 'application/yang-data+json',
            'Content-Type': 'application/yang-data+json'
        }

        try:
            response = requests.get(url, headers = headers, auth=self.auth, verify = False)
        except Exception as e:
            print(e)
            return {"status": 2, "result": str(e)}

        print(response.status_code)
        if (response.status_code == 200): # OK
            # convert JSON to dict
            dct = json.loads(response.text)
            return {"status": 0, "result": dct}

        # status_code != 200
        return {"status": 1, "result": response.status_code}

    def put_API(self, url, payload):

        headers = {
            'Accept': 'application/yang-data+json',
            'Content-Type': 'application/yang-data+json'
        }

        # convert dict to JSON
        data = json.dumps(payload)

        try:
            response = requests.put(url, headers = headers, auth=self.auth, data = data, verify = False)
        except Exception as e:
            print(e)
            return {"status": 2, "result": str(e)}

        print(response.status_code)
        return response.status_code

    def set_hostname(self, hostname):
        url = self.url + '/restconf/data/Cisco-IOS-XE-native:native/hostname'
        payload = {
            'Cisco-IOS-XE-native:hostname': hostname
        }
        return self.put_API(url, payload)

    def get_hostname(self):
        url = self.url + '/restconf/data/Cisco-IOS-XE-native:native/hostname'
        return self.get_API(url)

    def get_domain(self):
        url = self.url + '/restconf/data/Cisco-IOS-XE-native:native/ip/domain/name'
        return self.get_API(url)

    def get_interfaces(self):
        #url = self.url + '/restconf/data/ietf-interfaces:interfaces'
        url = self.url + '/restconf/data/Cisco-IOS-XE-native:native/interface'
        return self.get_API(url)

    def get_state(self):
        url = self.url + '/restconf/data/ietf-restconf-monitoring:restconf-state/capabilities'
        return self.get_API(url)

    def get_supported_yang_models(self):
        url = self.url + '/restconf/data/ietf-yang-library:modules-state'
        return self.get_API(url)

    def get_api_resource(self):
        url = self.url + '/restconf'
        return self.get_API(url)

    def get_root_resource(self):
        url = self.url + '/.well-known/host-meta'
        headers = {
            'Accept': 'application/yang-data+json',
            'Content-Type': 'application/yang-data+json'
        }

        try:
            response = requests.get(url, headers = headers, auth=self.auth, verify = False)
        except Exception as e:
            print(e)
            return {"status": 2, "result": str(e)}

        print(response.status_code)
        if (response.status_code == 200): # OK
            # convert JSON to dict
            pprint(response.headers)

        # status_code != 200
        #return {"status": 1, "result": response.status_code}


if __name__ == '__main__':
    print(__name__)
    c = C9200('172.20.1.252', 'admin', 'Sp4rk!01')


    '''
    ret = c.get_interfaces()
    if (ret['status'] == 0):
        pprint(ret['result'])
        GigabitEthernet = ret['result']['Cisco-IOS-XE-native:interface']['GigabitEthernet']
        for ge in GigabitEthernet:
            print("name: ", ge['name'])
    '''

    '''
    ret = c.get_domain()
    if (ret['status'] == 0):
        pprint(ret['result'])
        with open('C9200_native.json', 'w') as file:
            file.write(json.dumps(ret['result']))


    #ret = c.get_root_resource()
    '''

    '''
    ret = c.get_hostname()
    if (ret['status'] == 0):
        pprint(ret['result'])

    ret = c.get_domain()
    if (ret['status'] == 0):
        pprint(ret['result'])
    '''

    ret = c.get_arp()
    if (ret['status'] == 0):
        pprint(ret['result'])
