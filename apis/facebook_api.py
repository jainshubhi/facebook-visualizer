import urlparse2
import requests
import simplejson as json

from flask import url_for

class FacebookApi():

    # def extract_config(self):
    #     with open('facebook_api_config.json') as config:
    #         oauth_token = json.load(config)
    #     return oauth_token
    #
    # # generate FB API access token
    # def login(self):
    #     oauth_token = self.extract_config()
    #     token = requests.get('https://www.facebook.com/dialog/oauth?client_id=' + oauth_token['APP_ID'] + '&redirect_uri=www.shubhijain.com')

    def __init__(self, ACCESS_TOKEN):
        self._ACCESS_TOKEN=ACCESS_TOKEN

    @property
    def ACCESS_TOKEN(self):
        return self._ACCESS_TOKEN

    @ACCESS_TOKEN.setter
    def ACCESS_TOKEN(self, new_token):
        self._ACCESS_TOKEN = new_token
################################################################################
# Queries
################################################################################
    URL = 'https://graph.facebook.com/'

    # basic references
    def get_node(self, name, edge):
        return requests.get(URL + name + '?access_token=' + ACCESS_TOKEN).json()
