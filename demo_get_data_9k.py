#!/usr/bin/env python3

import yaml
from netmiko import ConnectHandler
import json
import demo_get_9k

HOST = '172.18.87.36'
PORT_SSH = 22
USER = 'vzhovtan'
PASS = 'RFFxlopina19**'
PLATFORM = 'cisco_xr'

line_card_file = "demo_seed_9k.yml"
config_file = "demo_config.yml"

def get_vaild_card(file_name):
    #taking the data from external YML file and creating list of valid line cards
    valid_line_card = []
    with open(file_name, 'r') as file:
        card_data = yaml.load(file, Loader=yaml.FullLoader)
        for key in card_data:
            valid_line_card.append(key)
    
    return valid_line_card
    
def get_lc_pattern(file_name):
    #taking the regular expression from external YML file
    reg_pattern = ""
    with open(file_name, 'r') as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
        for key in config_data:
            if "lc_pattern" in key:
                reg_pattern = config_data[key][0]
    
    return reg_pattern

def main():
    line_cards_9k = []
    interfaces_9k = []
    selected_platform_data = {}
    all_platform_data = {}

    valid_card_list = get_vaild_card(line_card_file)
    reg_pattern = get_lc_pattern(config_file)

    conn = ConnectHandler(device_type=PLATFORM, ip=HOST, port=PORT_SSH, username=USER, password=PASS)
    prompt = conn.find_prompt()

    line_cards_9k = demo_get_9k.platform_list_creation_9k(conn, valid_card_list, reg_pattern)
    interfaces_9k = demo_get_9k.interface_list_creation_9k(conn, line_cards_9k)
    selected_platform_data["line_cards"] = line_cards_9k
    selected_platform_data["interfaces"] = interfaces_9k
    all_platform_data[HOST] = selected_platform_data
    with open("outcome.json", "w") as file:
        file.write(json.dumps(all_platform_data))

if __name__ == '__main__':
    main()