from __future__ import unicode_literals, absolute_import, print_function
import json
import requests
import pprint
import bdblib
import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def task(env, sr):
    """
    Takes an SR number as input and returns the data from
    the BDB CSone API call.
    """
    pp = pprint.PrettyPrinter(indent=4)
    result = bdblib.TaskResult()
    if not re.match(r"\d{9}", sr):
        result.append({}, name='cscone_fields')
        return "SR does not seem be valid"
    attach_list = list_sr_attachments_csone(sr, env.cookies)
    result.append(attach_list, render=False, name='attach_list')
    result.append(pp.pformat(attach_list))
    return result


def list_sr_attachments_csone(sr, cookies):

    if not sr:
        logger.error("No SR provided")
        return {}

    bdb_csone_api = 'https://scripts.cisco.com/api/v2/attachments/{}'.format(sr)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.get(bdb_csone_api, headers=headers, cookies=cookies)

    if response.status_code != 200:
        logger.error("status_code %d when calling BDB CSone POST API: %s", response.status_code, response.text)
        return {}

    return json.loads(response.text)
