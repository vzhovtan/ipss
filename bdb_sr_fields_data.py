from __future__ import unicode_literals, absolute_import, print_function
import json
import requests
import pprint
import bdblib
import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def task(env, sr="", field_csv="", sr_csv=""):
    """
    Takes an SR number as input and returns the data from
    the BDB CSone API call.
    """
    pp = pprint.PrettyPrinter(indent=4)
    result = bdblib.TaskResult()
    if (not sr and not sr_csv) or (sr and sr_csv):
        result.append({}, name='cscone_fields')
        return "Need to provide sr or sr_csv parameters (not both)"
    if sr:
        fields = get_csone_sr_data(sr, field_csv, env.cookies)
        result.append(fields, render=False, name='cscone_fields')
        result.append(pp.pformat(fields))
        return result
    else:
        result_list = []
        sr_list = [sr.strip() for sr in sr_csv.split(",") if sr.strip()]
        for sr in sr_list:
            fields = get_csone_sr_data(sr, field_csv, env.cookies)
            fields["sr"] = sr
            result_list.append(fields)
        result.append(result_list, render=False, name='cscone_field_list')
        result.append(pp.pformat(result_list))
        return result


def get_csone_sr_data(sr, field_csv, cookies):

    if not sr:
        logger.error("No SR provided")
        return {}

    if field_csv:
        fields = [field.strip() for field in field_csv.split(",")]
    else:
        fields = get_csone_fields(sr, cookies)

    bdb_csone_api = 'https://scripts.cisco.com:443/api/v2/csone/{}'.format(sr)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post(bdb_csone_api, headers=headers, data=json.dumps(fields), cookies=cookies)

    if response.status_code != 200:
        logger.error("status_code %d when calling BDB CSone POST API: %s", response.status_code, response.text)
        return {}

    return json.loads(response.text)


def get_csone_fields(sr, cookies):
    bdb_csone_api = 'https://scripts.cisco.com:443/api/v2/csone'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.get(bdb_csone_api, headers=headers, cookies=cookies)

    if response.status_code != 200:
        logger.error("status_code %d when calling BDB CSone GET API: %s", response.status_code, response.text)
        return {}

    fields = json.loads(response.text)
    field_names = [field["name"] for field in fields]
    return field_names
