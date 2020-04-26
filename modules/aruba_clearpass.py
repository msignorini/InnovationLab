import requests
import json
import os
import time
import random
from configparser import ConfigParser
from pprint import pprint
from datetime import datetime


# return format
# {"status": <0, 1, 2>, "result": <something>}
# 0: ok
# 1: http error
# 2: exception

class ClearPass():

    def __init__(self, clearpass_fqdn, grant_type, client_id, client_secret,
                 username, password):

        # configuration parameters
        self.__access_token_lifetime = 8 * 60 * 60 # 8 hours
        self.__clearpass_fqdn = clearpass_fqdn
        self.__oauth_grant_type = grant_type
        self.__oauth_client_id = client_id
        self.__oauth_client_secret = client_secret
        self.__oauth_username = username
        self.__oauth_password = password
        self.__api_endpoint = "http://{}/api".format(self.__clearpass_fqdn)


    def get_access_token(self):
        """ Get access token """

        url = self.__api_endpoint + "/oauth"

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'grant_type': self.__oauth_grant_type,
            'username': self.__oauth_username,
            'password': self.__oauth_password,
            'client_id': self.__oauth_client_id,
            'client_secret': self.__oauth_client_secret
        }

        try:
            response = requests.post(url, headers = headers, json = data)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200): # OK
            # convert JSON to dict
            dct = json.loads(response.text)
            self.__auth = "{} {}".format(
                dct['token_type'],
                dct['access_token']
            )
            self.__token_timestamp = datetime.fromtimestamp(time.time())
            return {"status": 0, "result": response.status_code}

        # status_code != 200
        return {"status": 1, "result": response.status_code}


    def check_token_validity(self):
        """ Check if the access token is still valid """

        current_time = datetime.fromtimestamp(time.time())
        diff = (current_time - self.__token_timestamp).total_seconds()

         # if the access token is no longer valid generate new one
        if (diff > self.__access_token_lifetime):
            print("Refresh ClearPass access token")
            return self.get_access_token()

        return {"status": 0, "result": 0}


    def api_get(self, resource, params = None):
        """ Return the result of the get operation """

        """
        HTTP Status Code	Reason
        200	                OK
        401	                Unauthorized
        403	                Forbidden
        406	                Not Acceptable
        415	                Unsupported Media Type
        422	                Unprocessable Entity
        """

        url = self.__api_endpoint + resource

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.__auth
        }

        try:
            response = requests.get(url, headers = headers, params = params,
                                    verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200): # OK
            # convert JSON to dict
            dct = json.loads(response.text)
            return {"status": 0, "result": dct}

        # status_code != 200
        return {"status": 1, "result": response.status_code}


    def get_guest_account(self):
        """ Return the list of guest users """

        resource = "/guest"
        return self.api_get(resource)


    def does_guest_exist(self, key, value):
        """ Check if a guest exists """

        ret = self.get_guest_account()
        # check if get_guest_account() returned an error
        if (ret['status'] != 0):
            return ret

        # if there were no errors
        for data in ret['result']['_embedded']['items']:
            if data[key] == value:
                return {"status": 0, "result": True}
        return {"status": 0, "result": False}


    def get_session(self):
        """ Return the active session list """

        resource = "/session"

        querystring = {
            'filter': json.dumps({"acctstoptime": {"$exists": False}}),
            'calculate_count': 'true'
        }

        return self.api_get(resource, querystring)


    def active_session_disconnect(self, sessionid):
        """ Disconnect active session based on sessionid """

        """
        HTTP Status Code	Reason
        200	                OK
        400	                Bad Request
        401	                Unauthorized
        403	                Forbidden
        404	                Not Found
        406	                Not Acceptable
        415	                Unsupported Media Type
        422	                Unprocessable Entity
        """

        url = "{}/session/{}/disconnect".format(
            self.__api_endpoint,
            sessionid
        )

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.__auth
        }

        payload = {
            'confirm_disconnect': '1'
        }

        # convert dict to JSON
        data = json.dumps(payload)

        try:
            response = requests.post(url, data = data, headers = headers,
                                     verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200): # OK
            # convert JSON to dict
            dct = json.loads(response.text)
            return {"status": 0, "result": dct}

        # status_code != 200
        return {"status": 1, "result":response.status_code}


    def password_generator(self):
        """ Generate a password with length "passlen" without duplicate char """

        s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!$?"
        passlen = 6
        psw =  "".join(random.sample(s,passlen))
        return psw


    def post_guest_account(self, email):
        """ Craete a guest account """

        """
        HTTP Status Code	Reason
        201	                Created
        401	                Unauthorized
        403	                Forbidden
        406	                Not Acceptable
        415	                Unsupported Media Type
        422	                Unprocessable Entity
        """

        url = self.__api_endpoint + "/guest"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.__auth
        }

        # get UNIX timestamp
        tomorrow = int(time.time()) + 60 * 60 * 24
        psw = self.password_generator()

        # fields must be in the same order of API Explorer
        payload = {
            "email": email,
            "auto_send_smtp": 1, # ClearPass will send a receipt email
            "enabled": True,
            "expire_time": str(tomorrow),
            "password": psw,
            "role_id": 2,
            "username": email
        }

        # convert dict to JSON
        data = json.dumps(payload)

        try:
            response = requests.post(url, headers = headers, data = data,
                                     verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 201): # 201 Created
            # convert JSON to dict
            dct = json.loads(response.text)
            return {"status": 0, "result": [dct, psw]}

        # status_code != 201
        return {"status": 1, "result":response.status_code}


    def delete_guest_account(self, guest_id):
        """ Delete a guest account """

        """
        HTTP Status Code	Reason
        204	                No Content
        401	                Unauthorized
        403	                Forbidden
        404	                Not Found
        406	                Not Acceptable
        415	                Unsupported Media Type
        422	                Unprocessable Entity
        """

        url = "{}/guest/{}?change_of_authorization=true".format(
              self.__api_endpoint,
              guest_id
        )
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.__auth
        }

        try:
            response = requests.delete(url, headers = headers, verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if response.status_code == 204: # delete ok
            return {"status": 0, "result": response.status_code}

        # status_code != 204
        return {"status": 1, "result": response.status_code}


    def mark_compromised(self, mac_addr):
        """ Mark as compromized the endpoint with the specified mac addr """

        """
        HTTP Status Code	Reason
        200	                OK
        204	                No Content
        304	                Not Modified
        401	                Unauthorized
        403	                Forbidden
        404	                Not Found
        406	                Not Acceptable
        415	                Unsupported Media Type
        422	                Unprocessable Entity
        """

        url = "{}/endpoint/mac-address/{}".format(
            self.__api_endpoint,
            mac_addr
        )

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.__auth
        }

        payload = {
            'attributes': {
                'Compromised': True
            }
        }

        # convert dict to JSON
        data = json.dumps(payload)

        try:
            response = requests.patch(url, data = data, headers = headers,
                                      verify = False)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200): # OK
            #print("SUCCESS! Endpoint marked as compromised.\n")
            return {"status": 0, "result": response.status_code}

        # status_code != 200
        return {"status": 1, "result": response.status_code}


if (__name__ == '__main__'):
    print(__name__)
