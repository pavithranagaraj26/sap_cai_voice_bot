from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import uuid
import requests
import json
import os

class CAI:
    oAuthClientID = os.environ['oAuthClientID']
    oAuthClientSecret = os.environ['oAuthClientSecret']
    CAIreqToken = os.environ['CAIreqToken']
    def __init__(self):
        self.oAuthURL = 'https://sapcai-community.authentication.eu10.hana.ondemand.com/oauth/token'
        self.dialogURL = 'https://api.cai.tools.sap/build/v1/dialog'
        self.token = self._get_bearer()
    def _get_bearer(self):
        client = BackendApplicationClient(client_id=self.oAuthClientID)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=self.oAuthURL, client_id=self.oAuthClientID,
                client_secret=self.oAuthClientSecret)
        return token['access_token']
    def get_response(self,text):
        dialogPayload = {"message":{"type":"text","content":text},"conversation_id":str(uuid.uuid1())}
        dialogHeaders = {
                "Authorization": "Bearer " + self.token,
                "X-Token" : "Token " + self.CAIreqToken,
                "Content-Type" : "application/json"
            }
        dialogResponse = requests.post(self.dialogURL, data=json.dumps(dialogPayload), headers=dialogHeaders)
        if dialogResponse.status_code==requests.codes.ok:
            return dialogResponse.json()['results']['messages']
