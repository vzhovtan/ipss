__copyright__ = "Copyright (c) 2017 Cisco Systems. All rights reserved."

import os
import logging
try:
    from urllib.parse import urlencode
except ImportError:
     from urllib import urlencode

import requests
import json

import bdblib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def task(env, datafile):
    """BDB Task"""
    result = bdblib.TaskResult()
    items = json.loads(datafile)

    for item in items[:2]:
        download_file_to_session_folder(item['ticket_number'], item['filename'], env.cookies)
    result.append(bdblib.HTML("<p>Downloaded %s, %s</p>" % (item['ticket_number'], item['filename'])))
    return result


def download_file_to_session_folder(sr_id, filename, cookies):
    """Given a SR ID, filename and SSO Cookie, download the SR attachment to the users session folder"""
    url = "https://scripts.cisco.com:443/api/v2/attachments/{sr_id}/{url_encoded_filename}?overwrite=true"
    url_encoded_filename = urlencode({"f": filename})[2:]
    url = url.format(sr_id=sr_id, url_encoded_filename=url_encoded_filename)
    logger.debug("Downloading {} from {} to users session folder".format(filename, sr_id))
    r = requests.get(url, cookies=cookies)
    r.raise_for_status()
    logger.debug("File Download complete")
    return
