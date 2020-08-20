import yaml
import json
from bottle import *
from netmiko import ConnectHandler
import demo_get_9k

static_file_name = "demo_seed_9k.yml"

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
    conn = ConnectHandler(device_type="cisco_xr", ip=selected_host, port=22, username=user, password=pswd)
    prompt = conn.find_prompt()
    platform_kind = "Not supported platform"
    platform_kind_output = conn.send_command("show version")
    platform_kind_data = platform_kind_output.split("\n")
    for line in platform_kind_data:
        if "ASR9" in line:
            platform_kind = "ASR9000"

    return json.dumps(platform_kind)

@get('/platform_data')    # http://localhost:<port>/platform_data
def get_platform_data():
    response.content_type = 'application/json'
    input_data = json.load(request.body)
    selected_host = input_data['host']
    user = input_data['username']
    pswd = input_data['pswd']
    selected_platform_data = {}
    line_card_9k = []
    interfaces_9k = []

    conn = ConnectHandler(device_type="cisco_xr", ip=selected_host, port=22, username=user, password=pswd)
    prompt = conn.find_prompt()
    line_cards_9k = demo_get_9k.platform_list_creation_9k(conn, valid_card_list)
    interfaces_9k = demo_get_9k.interface_list_creation_9k(conn, line_cards_9k)
    selected_platform_data["line_cards"] = line_cards_9k
    selected_platform_data["interfaces"] = interfaces_9k

    return json.dumps(selected_platform_data)

if __name__ == '__main__':
    run(host='localhost', port=9600)