import requests
import simplejson as json


class FacebookApi():

    def extract_config(self):
        with open('facebook_api_config.json') as config:
            oauth_token = json.load(config)
        return oauth_token

    # generate FB API access token
    def generate_token(self):
        oauth_token = self.extract_config()
        token = requests.get('https://graph.facebook.com/endpoint?key=value&access_token=' + oauth_token['APP_ID'] + '|' + oauth_token['APP_SECRET']).json()
        return token['access_token']
