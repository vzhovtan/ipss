"""
API access to the data gathering module

__copyright__ = "Copyright (c) 2018-2020 aorel, stoporko, vfilippo, vzhovtan@Cisco Systems. All rights reserved."
__author__ = 'vzhovtan'
"""

import yaml
import json
from bottle import *
from netmiko import ConnectHandler
import get_55
import get_9k

static_file_name = "seed.yml"

def static_data_processing(file_name):
    #taking the data from external YML file and creating list of valid line cards for all platforms
    valid_line_card = []
    with open(file_name, 'r') as file:
        seed_data = yaml.load(file, Loader=yaml.FullLoader)
        for key in seed_data:
            valid_line_card.append(key)
    return valid_line_card

valid_card_list = static_data_processing(static_file_name)

@get('/')    # http://localhost:<port>
def welcome():
    response.set_header('Vary', 'Accept')
    response.content_type = 'application/json'
    return 'REST API for Intelligent Power Saving Solution (IPSS)'

@get('/platform')    # http://localhost:<port>/releasesplatform
def get_platform():
    response.content_type = 'application/json'
    input_data = json.load(request.body)
    selected_host = input_data['host']
    user = input_data['username']
    pswd = input_data['pswd']
    release_list = []
    conn = ConnectHandler(device_type="cisco_xr", ip=selected_host, port=22, username=user, password=pswd)
    prompt = conn.find_prompt()
    platform_kind = ""
    platform_kind_output = conn.send_command("show version")
    platform_kind_data = platform_kind_output.split("\n")
    for line in platform_kind_data:
        if "NCS-5500" in line:
            platform_kind = "NCS5500"
        elif "ASR9" in line:
            platform_kind = "ASR9000"

    return json.dumps(platform_kind)

@get('/platform_data')    # http://localhost:<port>/platform_data
def get_platform_data():
    response.content_type = 'application/json'
    input_data = json.load(request.body)
    selected_host = input_data['host']
    user = input_data['username']
    pswd = input_data['pswd']
    selected_platform = input_data['platform']
    selected_platform_data = {}
    conn = ConnectHandler(device_type="cisco_xr", ip=selected_host, port=22, username=user, password=pswd)
    prompt = conn.find_prompt()
    if selected_platform == "NCS5500":
        line_card_55 = []
        interfaces_55 = []
        line_card_55 = get_55.platform_list_creation_55(conn)
        interfaces_55 = get_55.interface_list_creation_55(conn)
        selected_platform_data["line_cards"] = line_card_55
        selected_platform_data["interfaces"] = interfaces_55
    elif selected_platform == "ASR9000":
        line_card_9k = []
        interfaces_9k = []
        slices_9k = []
        line_card_9k = get_9k.platform_list_creation_9k(conn, valid_card_list)
        interfaces_9k = get_9k.interface_list_creation_9k(conn, line_card_9k)
        slices_9k = get_9k.slice_list_creation_9k(conn)
        selected_platform_data["line_cards"] = line_card_9k
        selected_platform_data["interfaces"] = interfaces_9k
        selected_platform_data["slices"] = interfaces_9k

    return json.dumps(selected_platform_data)

if __name__ == '__main__':
    run(host='localhost', port=9600)