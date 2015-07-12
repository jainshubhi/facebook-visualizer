import requests
import simplejson as json

from flask import url_for

class FacebookApi():

    def extract_config(self):
        with open('facebook_api_config.json') as config:
            oauth_token = json.load(config)
        return oauth_token

    # generate FB API access token
    def generate_token(self):
        oauth_token = self.extract_config()
        token = requests.get('https://www.facebook.com/dialog/oauth?client_id=' + oauth_token['APP_ID'] + '&redirect_uri=' + url_for('show_friends')).json()
        return token['access_token']
