import requests
import datetime
import os
import json
from configparser import ConfigParser
from pprint import pprint

# return format
# {"status": <0, 1, 2>, "result": <something>}
# 0: ok
# 1: http error
# 2: exception

class Telegram:

    def __init__(self, token, whitelist):
        self.token = token
        self.whitelist = whitelist
        self.api_url = "https://api.telegram.org/bot{}/".format(self.token)

    def get_updates(self, offset=None, timeout=30):
        """ Get updates from Telegram Bot """

        url = '{}getUpdates'.format(self.api_url)
        params = {
            'timeout': timeout,
            'offset': offset
        }

        try:
            response = requests.get(url, params)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if (response.status_code == 200):
            # parse the JSON string into native Python data
            dct = json.loads(response.text)
            return {"status": 0, "result": dct['result']}

        return {"status": 1, "result": response.status_code}

    def send_message(self, chat_id, text):
        ''' Use this method to send text messages.
        On success, the sent Message is returned. '''

        url = self.api_url + 'sendMessage'
        params = {
            'chat_id': chat_id,
            'text': text
        }

        try:
            response = requests.get(url, params)
        except Exception as e:
            return {"status": 2, "result": str(e)}

        if response.status_code == 200: # send ok
            dct = json.loads(response.text)
            return {"status": 0, "result": dct}

        return {"status": 1, "result": response.status_code}

    def is_whitelisted(self, sender_id):
        ''' Check if the sender id is whitelisted '''
        for value in self.whitelist:
            if value["id"] == sender_id:
                return True
        return False

if __name__ == '__main__':
    print(__name__)
