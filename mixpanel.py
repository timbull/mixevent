#!/usr/bin/python

"""
Logs an event to MixPanel
"""

import json
import base64
import time
import urllib
import httplib
import urlparse
TIMEOUT = 20

from trunkly.settings import MIXPANEL_TOKEN

def http(url, params=None, http_method='GET'):
    ''' Low level HTTP library '''

    headers = {}
    #split the URL into something useful!
    parts = urlparse.urlparse(url)
    scheme, host, uri = parts[:3]

    if scheme == "HTTPS":
        con = httplib.HTTPSConnection(host, timeout = TIMEOUT)
    else:
        con = httplib.HTTPConnection(host, timeout = TIMEOUT)

    headers['User-agent'] = 'http://trunk.ly'

    post_data = None
    if http_method in ('POST', 'PUT') :
        # Add the additional content type headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        post_data = urllib.urlencode(params)
    else: # GET or DELETE
        if params:
            post_data = urllib.urlencode(params)
            uri = uri + '?' + post_data

    con.request(http_method, uri, post_data, headers)
    response = con.getresponse()
    data = response.read()
    con.close()

    return response.status, data

def track(event):
    """ Track a mixpanel event """

    params = {'data': base64.b64encode(json.dumps(event))}
    request_url = "http://api.mixpanel.com/track/"
    
    status, result = http(request_url, params, 'POST')
    
    if status == 200:
        # result is a 1 or 0 (1 is True)
        return bool(result)
    else:
        return False


def build_event(event, username=None, ip_address=None, properties={}):
    """ Returns a JSON encoded object to pass to the mixevent queue
        event = string
        username = username if one is provided
        ip = ip if one is provided.
        You need to provide one or the other (actually the event will probably
        be tracked anyway but you should identify who triggered it).
        properties a dictionary of properties e.g. {'account': 'paid} etc.
        
        NOTE: When getting the IP address to use in calling this function,
        it might be REMOTE_ADDR, but in a production setup (for example behind
        NGINX) this will be 127.0.0.1 (localhost).  In this instance, make sure
        you have configured NGINX to forward the IP and use this
        e.g. HTTP_X_REAL_IP
    """
    
    event_dict = {'event' : event,
            'properties': properties}
    
    if username:
        event_dict['properties']['distinct_id'] = username
    if ip_address:
        event_dict['properties']['ip'] = ip_address
    event_dict['properties']['token'] = MIXPANEL_TOKEN
    event_dict['properties']['time'] = int(time.time())
    
    return event_dict