# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set syntax=python:
#########################
# (c) JR, 2022          #
#########################
from configparser import ConfigParser, ExtendedInterpolation
import requests
import json

global cookie

config = ConfigParser(interpolation=ExtendedInterpolation())

try:
    config.read('dspace_api/api_config.ini')
except Exception as e:
    raise e



print("CONFIG: {}".format(config))

def login():
    
    headers = {'Accept': 'application/json', 'Accept-Charset': 'UTF-8'}
    
    email = config.get('LOGIN', 'username')
    password = config.get('LOGIN','password')

    data = {"email":email,"password":password}
    
    url = config.get('GENERAL','api_root') + config.get('LOGIN', 'endpoint')
    
    request = requests.post(url=url, headers=headers, data=data)

    if request.status_code == requests.codes.ok:
        
        return request.cookies.get('JSESSIONID')
    else:
        raise Exception('Failed to login to DSpace API:\n'+'Status code ' + str(request.status_code)+': '+request.reason)

def create_metadataentry_object(meta_dict: dict, meta_field: str):
    # structure and contents  of metadataentry object: 
    # https://wiki.lyrasis.org/display/DSDOC6x/REST+API#RESTAPI-MetadataEntryO
    # [{
    #   "key": "[schema].[element](.[qualifier]",
    #   "value": "Some value",
    #   "language": "some_language" or "" for no language
    # }]
    metadata_entry = dict()
    metadata_entry.update(
        {
            "key": meta_field,
            "value": meta_dict[meta_field],
            "language": ""
        }
    )
    metadata_entry_object = [metadata_entry]
    
    return json.dumps(metadata_entry_object)

def create_request_url(endpoint: str, dso_identifier: str, type: str = 'metadata'):
    url = None
    
    if type == 'metadata':
        
        if endpoint == 'items':
            url = '/'.join([config.get("GENERAL", "api_root"),endpoint, dso_identifier, type])
            # curl = 'curl -4 --cookie ' + cookie + ' -H "accept: application/json" -H "Content-Type: application/json -X PUT "' + url + '"' + ' -d '
            
        else:
            raise NotImplementedError("Cannot create request for other endpoint than 'items'.")
    else:
        raise NotImplementedError("Cannot create other request type than 'metadata'")

    return url

def request_update_metadata(request_url: str, metadata_entry):

    headers = {'accept': 'application/json',
            'Content-Type': 'application/json'}

    try:
        response = requests.put(cookies = {"JSESSIONID": cookie}, headers=headers,url=request_url, data=metadata_entry)
    
        if response.status_code == 401:
            try:
                cookie = login()
                response = requests.put(cookies = {"JSESSIONID": cookie}, headers=headers,url=request_url, data=metadata_entry)
            except Exception as e:
                raise e
        else:
            response.raise_for_status()

        message = "Status code: {} \t Text: {}".format(response.status_code, response.text)
        return message

    except Exception as e:
        raise e


try:
    cookie = login()

    if cookie is None:
        raise Exception("No JSESSIONID - login to DSpace API not successfull") 
except Exception as e:
    raise e
