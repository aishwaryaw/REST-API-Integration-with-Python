#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import base64 
import datetime
from urllib.parse import urlencode
import pprint


# In[2]:


class SpotifyAPI():
    client_id = None
    client_secret = None
    access_token = None
    access_token_expires_in = datetime.datetime.now()
    access_token_did_expire = False
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id , client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
    
    def get_client_credentials(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None or client_secret == None:
            raise Exception("You must set client id and client secret")
        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_base64 = base64.b64encode(client_creds.encode())
        return client_creds_base64
    
    def get_token_header(self):
        client_creds_base64 = self.get_client_credentials()
        token_header = {
        "Authorization": f"Basic {client_creds_base64.decode()}"  # <base64 encoded client_id:client_secret>
        }
        return token_header
          
        
    def get_token_data(self):
        return {
                "grant_type":"client_credentials"
                }
    
    
    def perform_auth(self):
        token_data = self.get_token_data()
        token_header = self.get_token_header()
        r = requests.post(self.token_url, data = token_data, headers =token_header)
        if r.status_code not in range(200,299):
#             print(r.status_code)
            return False
        
        data = r.json()
        access_token = data['access_token']
        expires_in = data['expires_in']
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(seconds = expires_in) # to get the time of expiration 
        self.access_token = access_token
        self.access_token_expires_in = expires
        self.access_token_did_expire = expires < now # token expired = if time of expiration is less than current time 
        return True
      
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires_in
        now = datetime.datetime.now()
        if now > expires:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token
        
    
    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
               "Authorization" : f"Bearer {access_token}"     
        }
        return headers
    
    def get_resource(self ,lookup_id , resource_type="artist" , version="v1" ):
        headers = self.get_resource_header()
        lookup_url = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        r = requests.get(lookup_url , headers= headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()
    
    def get_album(self, _id):
        return self.get_resource(_id , resource_type="albums")
        
    def get_artist(self, _id):
        return self.get_resource(_id , resource_type="artists") 
    
    def base_search(self, query_params):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers = headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()
        
    def search(self, query=None, operator=None, operator_query=None, search_type='artist' ):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k,v in query.items()])
            print(query)
            print(operator, operator_query)
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        print(query_params)
        return self.base_search(query_params)
        
           


# In[ ]:




