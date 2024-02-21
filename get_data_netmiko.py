"""
Gathering data from devices using Netmiko library

__copyright__ = "Copyright (c) 2018-2020 aorel, stoporko, vfilippo, vzhovtan@Cisco Systems. All rights reserved."
__author__ = 'vzhovtan'
"""

import os
import yaml
import json
from netmiko import ConnectHandler
import get_55
import get_9k


HOST = 'ipv4'
PORT_SSH = 22
USER = os.getenv("USER")
PASS = os.getenv("PASSWORD")
PLATFORM = 'cisco_xr'
static_file_name = "seed.yml"

line_card_55 = []
interfaces_55 = []
line_cards_9k = []
interfaces_9k = []
slices_9k = []

def static_data_processing(file_name):
    # taking the data from external YML file and creating list of valid line cards for all platforms
    valid_line_card = []
    with open(file_name, 'r') as file:
        seed_data = yaml.load(file, Loader=yaml.FullLoader)
        for key in seed_data:
            valid_line_card.append(key)
    
    return valid_line_card

def platform_kind_verification(connection):
    # taking 'show version' output and extracting platform type
    platform_kind = ""
    platform_kind_output = connection.send_command("show version")
    platform_kind_data = platform_kind_output.split("\n")
    for line in platform_kind_data:
        if "NCS-5500" in line:
            platform_kind = "NCS5500"
        elif "ASR9" in line:
            platform_kind = "ASR9000"

    return platform_kind

if __name__ == "__main__":
    conn = ConnectHandler(device_type=PLATFORM, ip=HOST, port=PORT_SSH, username=USER, password=PASS)
    prompt = conn.find_prompt()

    valid_card_list = static_data_processing(static_file_name)
    platform_kind = platform_kind_verification (conn)
    if platform_kind == "NCS5500":
        line_card_55 = get_55.platform_list_creation_55(conn)
        interfaces_55 = get_55.interface_list_creation_55(conn)
        json.dumps(line_card_55)
        json.dumps(interfaces_55)
    elif platform_kind == "ASR9000":
        line_cards_9k = get_9k.platform_list_creation_9k(conn, valid_card_list)
        interfaces_9k = get_9k.interface_list_creation_9k(conn, line_cards_9k)
        slices_9k = get_9k.slice_list_creation_9k(conn)
        json.dumps(line_cards_9k)
        json.dumps(interfaces_9k)
        json.dumps(slices_9k)