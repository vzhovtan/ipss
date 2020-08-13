import re
import yaml
from netmiko import ConnectHandler

HOST = '10.48.42.59'
PORT_SSH = 22
USER = 'iox'
PASS = 'l4b'
PLATFORM = 'cisco_xr'

interface_list = []
platform_list = []

interface_pattern = re.compile("Gi\d{1,2}\/.*|TE.*|Hu.*|Fo.*")
subint_pattern = re.compile(".*ARPA.*")

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
    if "Slice" in line_card or "IOS XR RUN" in line_card:
        platform_list.append(line_card.split())
print(platform_list)
