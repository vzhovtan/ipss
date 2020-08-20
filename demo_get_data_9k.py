import yaml
from netmiko import ConnectHandler
import json
import demo_get_9k

HOST = 'ipv4'
PORT_SSH = 22
USER = 'user'
PASS = 'pswd**'
PLATFORM = 'cisco_xr'
static_file_name = "demo_seed_9k.yml"

def static_data_processing(file_name):
    #taking the data from external YML file and creating list of valid line cards for all platforms
    valid_line_card = []
    with open(file_name, 'r') as file:
        seed_data = yaml.load(file, Loader=yaml.FullLoader)
        for key in seed_data:
            valid_line_card.append(key)
    
    return valid_line_card

line_cards_9k = []
interfaces_9k = []
selected_platform_data = {}
all_platform_data = {}

conn = ConnectHandler(device_type=PLATFORM, ip=HOST, port=PORT_SSH, username=USER, password=PASS)
prompt = conn.find_prompt()

valid_card_list = static_data_processing(static_file_name)
line_cards_9k = demo_get_9k.platform_list_creation_9k(conn, valid_card_list)
interfaces_9k = demo_get_9k.interface_list_creation_9k(conn, line_cards_9k)
selected_platform_data["line_cards"] = line_cards_9k
selected_platform_data["interfaces"] = interfaces_9k
all_platform_data[HOST] = selected_platform_data
with open("outcome.json", "w") as file:
    file.write(json.dumps(selected_platform_data))
