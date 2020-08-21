import yaml
from netmiko import ConnectHandler
import json
import demo_get_9k

HOST = 'ipv4'
PORT_SSH = 22
USER = 'user'
PASS = 'pswd'
PLATFORM = 'cisco_xr'
static_file_name = "demo_seed_9k.yml"

line_cards_9k = []
interfaces_9k = []
selected_platform_data = {}
all_platform_data = {}

def get_vaild_card(file_name):
    #taking the data from external YML file and creating list of valid line cards
    valid_line_card = []
    with open(file_name, 'r') as file:
        seed_data = yaml.load(file, Loader=yaml.FullLoader)
        for key in seed_data:
            if "pattern" not in key:
                valid_line_card.append(key)
    
    return valid_line_card
    
def get_lc_pattern(file_name):
    #taking the regular expression from external YML file
    reg_pattern = ""
    with open(file_name, 'r') as file:
        seed_data = yaml.load(file, Loader=yaml.FullLoader)
        for key in seed_data:
            if "pattern" in key:
                reg_pattern = seed_data[key][0]
    
    return reg_pattern

valid_card_list = get_vaild_card(static_file_name)
reg_pattern = get_lc_pattern(static_file_name)

conn = ConnectHandler(device_type=PLATFORM, ip=HOST, port=PORT_SSH, username=USER, password=PASS)
prompt = conn.find_prompt()

line_cards_9k = demo_get_9k.platform_list_creation_9k(conn, valid_card_list, reg_pattern)
interfaces_9k = demo_get_9k.interface_list_creation_9k(conn, line_cards_9k)
selected_platform_data["line_cards"] = line_cards_9k
selected_platform_data["interfaces"] = interfaces_9k
all_platform_data[HOST] = selected_platform_data
with open("outcome.json", "w") as file:
    file.write(json.dumps(all_platform_data))
