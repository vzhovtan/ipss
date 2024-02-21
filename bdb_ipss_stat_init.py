from __future__ import unicode_literals, absolute_import, print_function
import bdblib
import os
import csv
import json
import pprint
import logging
import requests
try:
    from urllib.parse import urlencode
except ImportError:
     from urllib import urlencode

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

def task(env, list_sr):
    """
    Takes an list of SRs as input and returns the data from
    the BDB CSone API call.
    """

    list_sr = []
    with open('9k_lightning.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            list_sr.append(row[0])

    pp = pprint.PrettyPrinter(indent=4)
    result = bdblib.TaskResult()
    for sr in list_sr:
        subtech = get_csone_sr_data(sr, env.cookies)
        if "ASR 9000" in subtech['Sub_Technology_Text__c']:
            attach_list = get_csone_list_sr_attachments(sr, env.cookies)
            for file_item in attach_list:
                if "showtech-generic" in file_item['fileName']:
                    result_dict = {}
                    result_dict['srId'] = sr
                    result_dict['fileName'] = file_item['fileName']
                    #get_attachment_file_to_session_folder(sr, file_item['fileName'], env.cookies)
                    result.append(pp.pformat(result_dict))

    return result

def get_csone_sr_data(sr, cookies):
    "Given a SR ID and SSO Cookie, get selected metadat for SR (fileds)"
    fields = ["Sub_Technology_Text__c"]
    bdb_csone_api = 'https://scripts.cisco.com:443/api/v2/csone/{}'.format(sr)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post(bdb_csone_api, headers=headers, data=json.dumps(fields), cookies=cookies)

    if response.status_code != 200:
        logger.error("status_code %d when calling BDB CSone POST API: %s", response.status_code, response.text)
        return {}

    return json.loads(response.text)

def get_csone_list_sr_attachments(sr, cookies):
    "Given a SR ID and SSO Cookie, get list of attachment"
    bdb_csone_api = 'https://scripts.cisco.com/api/v2/attachments/{}'.format(sr)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.get(bdb_csone_api, headers=headers, cookies=cookies)

    if response.status_code != 200:
        logger.error("status_code %d when calling BDB CSone POST API: %s", response.status_code, response.text)
        return {}

    return json.loads(response.text)


def get_attachment_file_to_session_folder(sr_id, filename, cookies):
    "Given a SR ID, filename and SSO Cookie, download the SR attachment to the users session folder"
    bdb_csone_api = "https://scripts.cisco.com:443/api/v2/attachments/{sr_id}/{url_encoded_filename}?overwrite=true"
    url_encoded_filename = urlencode({"f": filename})[2:]
    bdb_csone_api = bdb_csone_api.format(sr_id=sr_id, url_encoded_filename=url_encoded_filename)
    response = requests.get(bdb_csone_api, cookies=cookies)
    response.raise_for_status()
    return    