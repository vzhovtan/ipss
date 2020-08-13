import re
import yaml
from netmiko import ConnectHandler

HOST = '10.48.32.89'
PORT_NC = 830
PORT_SSH = 22
USER = 'iox'
PASS = 'l4b'
PLATFORM = 'cisco_xr'

valid_line_card = []
interface_list = []
platform_list = []
slice_list = []
card_list = []
slice_struct_data = []

interface_pattern = re.compile("Gi\d{1,2}\/.*|TE.*|Hu.*")
subint_pattern = re.compile(".*ARPA.*")
lc_type_pattern = re.compile("(\d\/\d{1,2}\/CPU.?\s+)(A9.+?-[^ \t\r\n\f].*?)(\s|-)")

#grabbing static data and creating list of valid line cards
with open("seed.yml", 'r') as file:
    seed_data = yaml.load(file, Loader=yaml.FullLoader)

for key in seed_data:
    valid_line_card.append(key)
print(valid_line_card)

conn = ConnectHandler(device_type=PLATFORM, ip=HOST, port=PORT_SSH, username=USER, password=PASS)
prompt = conn.find_prompt()

interface_output = conn.send_command("show interface brief")
interface_data = interface_output.split("\n")
for interface in interface_data:
     if interface_pattern.search(interface.strip()) and subint_pattern.search(interface.strip()):
        interface_status = interface.strip().split()
        if interface_status[1] =="admin-down" and interface_status[2] == "admin-down":
             interface_list.append(interface_status[:3])
        elif interface_status[1] =="down" and interface_status[2] == "down":
             interface_list.append(interface_status[:3])
print(interface_list)

platform_output = conn.send_command("show platform")
platform_data = platform_output.split("\n")
for line_card in platform_data:
     lc_type = lc_type_pattern.search(line_card)
     if lc_type:
          if lc_type.group(2) in valid_line_card:
               platform_list.append(line_card.strip().split())
print(platform_list)

slice_output = conn.send_command("show platform slices")
slice_data = slice_output.split("\n")
for slice in slice_data:
    if "Power" in slice and "On" in slice:
        slice_list.append(slice.strip().split())
for item in slice_list:
    if "CPU" in item[0] and item[0] not in card_list:
        card_num = item[0]
        card_list.append(item[0])
        slice_struct_data.append(item)
    else:
        item.insert(0, card_num)
        slice_struct_data.append(item)
print(slice_struct_data)


