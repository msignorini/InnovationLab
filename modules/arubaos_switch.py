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

class ArubaOS_Switch():

    def __init__(self, ip, username, password):
        self.credentials = {
            'userName': username,
            'password': password
        }
        self.url = "http://{}/rest/v3/".format(ip)

    def login(self):
        """ Obtain cookie """

        data = json.dumps(self.credentials)
        url = '{}login-sessions'.format(self.url)

        try:
            response = requests.post(url, data = data, timeout = 1)
        except Exception as e:
            return {"status": 2, "result": str(e)}


        if response.status_code == 201: # login ok
            self.headers = {
                'cookie': response.json()['cookie']
            }
            return {"status": 0, "result": response.status_code}

        return {"status": 1, "result": response.status_code}

    def logout(self):
        """ Logout from switch """

        url = '{}login-sessions'.format(self.url)

        try:
            response = requests.delete(url, headers = self.headers,
                timeout = 1, verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if response.status_code == 204: # logout ok
            return {"status": 0, "result": response.status_code}

        return {"status": 1, "result": response.status_code}

    def send_BATCH_command(self, cmd):
        """ Send a batch of CLI command to switch """

        # commands must be bytes not a string
        command_bytes = cmd.encode()
        # perform encoding to base64
        base64_command = base64.b64encode(command_bytes)
        # bytes must be decoded as a utf-8 string for the dict.
        # It is base64 but as a unicode string
        command_dict = {
            'cli_batch_base64_encoded': base64_command.decode('utf-8')
        }

        data = json.dumps(command_dict)
        url = '{}cli_batch'.format(self.url)

        try:
            response = requests.post(url, headers = self.headers,
                                     data = data, timeout = 1, verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        # checks for error
        if response.status_code != 202:
            return {"status": 1, "result": response.status_code}

        # convert the result in a readable string
        ret_base64 = response.json()
        return {"status": 0, "result": ret_base64}

    def send_CLI_command(self, cmd):
        """ Send a specific CLI command to switch """

        command = {
            'cmd': cmd
        }
        data = json.dumps(command)
        url = '{}cli'.format(self.url)

        try:
            response = requests.post(url, headers = self.headers,
                                     data = data, timeout = 1, verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        # checks for error
        if response.status_code != 200:
            return {"status": 1, "result": response.status_code}

        # convert the result in a readable string
        ret_base64 = response.json()['result_base64_encoded']
        decoded = base64.b64decode(ret_base64).decode('utf-8')
        return {"status": 0, "result": decoded}

    def show_running_config(self):
        """ Return the switch running config """

        cmd = "show running-config"
        return self.send_CLI_command(cmd)

    def show_vlans(self):
        """ Return the switch VLAN database """

        cmd = "show vlans"
        return self.send_CLI_command(cmd)

    def show_port_access(self):
        """ Return the authenticated clients """

        cmd = "show port-access clients"
        return self.send_CLI_command(cmd)

if __name__ == '__main__':
    print(__name__)
