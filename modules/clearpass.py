import requests
import json
import os
from configparser import ConfigParser
from pprint import pprint
import time
from datetime import datetime
import random

# return format
# {"status": <0, 1, 2>, "result": <something>}
# 0: ok
# 1: http error
# 2: exception

class ClearPass():

    def __init__(self, clearpass_fqdn, grant_type, client_id, client_secret,
                 username, password):

        # configuration parameters
        self.access_token_lifetime = 8 * 60 * 60 # 8 hours
        self.clearpass_fqdn = clearpass_fqdn
        self.oauth_grant_type = grant_type
        self.oauth_client_id = client_id
        self.oauth_client_secret = client_secret
        self.oauth_username = username
        self.oauth_password = password
        self.API_ENDPOINT = "http://{}/api/".format(self.clearpass_fqdn)

    def get_access_token(self):
        """ Get access token """

        url = "{}oauth".format(self.API_ENDPOINT)

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'grant_type': self.oauth_grant_type,
            'username': self.oauth_username,
            'password': self.oauth_password,
            'client_id': self.oauth_client_id,
            'client_secret': self.oauth_client_secret
        }

        try:
            response = requests.post(url, headers = headers, json = data)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200): # ok
            # parse the JSON string into native Python data
            dct = json.loads(response.text)
            self.API_AUTH = "{} {}".format(
                dct['token_type'], dct['access_token']
            )
            self.TOKEN_TIMESTAMP = datetime.fromtimestamp(time.time())
            return {"status": 0, "result": response.status_code}

        return {"status": 1, "result": response.status_code}

    def check_token_validity(self):
        ''' Check if the access token is still valid '''

        current_time = datetime.fromtimestamp(time.time())
        diff = (current_time - self.TOKEN_TIMESTAMP).total_seconds()

        # if the access token is no longer valid generate new one
        if (diff > self.access_token_lifetime):
            print("Refresh ClearPass access token")
            return self.get_access_token()

        return {"status": 0, "result": 0}

    def get_guest_account(self):
        """ Return the list of guest users """

        url = "{}guest".format(self.API_ENDPOINT)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.API_AUTH
        }

        try:
            response = requests.get(url, headers = headers, verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200): # ok
            # parse the JSON string into native Python data
            dct = json.loads(response.text)
            return {"status": 0, "result": dct}

        return {"status": 1, "result": response.status_code}

    def does_guest_exist(self, key, value):
        """ Check if a guest exists """

        ret = self.get_guest_account()
        # check if get_guest_account() returned an error
        if ret['status'] != 0:
            return ret

        # if there were no errors
        for data in ret['result']['_embedded']['items']:
            if data[key] == value:
                return {"status": 0, "result": True}
        return {"status": 0, "result": False}

    def password_generator(self):
        """ Generate a password with length "passlen" without duplicate char """

        s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!$?"
        passlen = 6
        psw =  "".join(random.sample(s,passlen))
        return psw

    def post_guest_account(self, email):
        """ Craete a guest account """

        url = "{}guest".format(self.API_ENDPOINT)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.API_AUTH
        }

        # get UNIX timestamp
        tomorrow = int(time.time()) + 60 * 60 * 24
        psw = self.password_generator()

        # fields must be in the same order of API Explorer
        d = {
            "email":email,
            "auto_send_smtp": 1, # ClearPass will send a receipt email
            "enabled": True,
            "expire_time": str(tomorrow),
            "password": psw,
            "role_id": 2,
            "username": email
        }

        # convert dct to JSON
        data = json.dumps(d)

        try:
            response = requests.post(url, headers = headers, data = data,
                                     verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 201): # 201 Created
            # parse the JSON string into native Python data
            dct = json.loads(response.text)
            return {"status": 0, "result": [dct, psw]}

        return {"status": 1, "result":response.status_code}

    def delete_guest_account(self, guest_id):
        """ Delete a guest account """

        url = "{}guest/{}?change_of_authorization=true".format(
              self.API_ENDPOINT, guest_id
        )
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.API_AUTH
        }

        try:
            response = requests.delete(url, headers = headers, verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if response.status_code == 204: # delete ok
            return {"status": 0, "result": response.status_code}

        return {"status": 1, "result": response.status_code}

if __name__ == '__main__':
    print(__name__)
