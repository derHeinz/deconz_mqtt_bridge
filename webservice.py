#!/usr/bin/python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen, build_opener, HTTPHandler, Request
import json
import datetime

def get_value_from(url):
    # need to have this header all other headers are ignored!
    req = Request(url)
    return urlopen(req)

def post_value_to(url, value):
    # need to have this header all other headers are ignored!
    header = {"Content-Type":"text/plain"}
    params_bytes = _params_from_value(value)
    req = Request(url, params_bytes, header)
    return urlopen(req)
    
def put_value_to(url, value):
    # need to have this header all other headers are ignored!
    header = {"Content-Type":"text/plain"}
    params_bytes = _params_from_value(value)
    req = Request(url, params_bytes, header)
    req.get_method = lambda: 'PUT'
    opener = build_opener(HTTPHandler)
    return opener.open(req).read()

def _params_from_value(value):
    if isinstance(value, datetime.datetime):
        time_string = value.strftime("%Y-%m-%dT%H:%M:%S")
        return time_string.encode('utf-8')
    else:
        return value.encode('utf-8')