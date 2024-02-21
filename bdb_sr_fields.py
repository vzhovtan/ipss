from __future__ import unicode_literals, absolute_import, print_function
import json
import requests
import pprint
import bdblib
import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def task(env):
    """
    Takes an SR number as input and returns the data from
    the BDB CSone API call.
    """
    pp = pprint.PrettyPrinter(indent=4)
    result = bdblib.TaskResult()
    fields = get_csone_sr_fields(env.cookies)
    result.append(fields, render=False, name='cscone_fields')
    result.append("\n".join(fields))
    return result


def get_csone_sr_fields(cookies):
    bdb_csone_api = 'https://scripts.cisco.com:443/api/v2/csone'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.get(bdb_csone_api, headers=headers, cookies=cookies)

    if response.status_code != 200:
        logger.error("status_code %d when calling BDB CSone GET API: %s", response.status_code, response.text)
        return {}

    fields = json.loads(response.text)
    field_names = [field["name"] for field in fields]
    return field_names