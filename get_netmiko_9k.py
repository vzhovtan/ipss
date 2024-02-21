"""
Gathering data from devices using Netmiko library from ASR9000 platforms only

__copyright__ = "Copyright (c) 2018-2020 aorel, stoporko, vfilippo, vzhovtan@Cisco Systems. All rights reserved."
__author__ = 'vzhovtan'
"""

import os
import re
import yaml
from netmiko import ConnectHandler

HOST = 'ipv4'
PORT_SSH = 22
USER = os.getenv("USER")
PASS = os.getenv("PASSWORD")
PLATFORM = 'cisco_xr'

valid_line_card = []
interface_list = []
platform_list = []
slice_list = []
card_list = []
slice_struct_data = []
final_interface_list = []
platform_type = ""

interface_pattern = re.compile("Gi\d{1,2}\/.*|TE.*|Hu.*|Fo.*")
subint_pattern = re.compile(".*ARPA.*")
#lc_type_pattern = re.compile("(\d\/\d{1,2}\/CPU.?\s+)(A9.+?-[^ \t\r\n\f].*?)(\s|-)")
lc_type_pattern = re.compile("(A9.+?-[^ \t\r\n\f].*GE)|(A9.+?-MOD.*-)")
lc_int_number_pattern = re.compile("(\d\/\d).*")

#grabbing static data and creating list of valid line cards
with open("seed_9k.yml", 'r') as file:
    seed_data = yaml.load(file, Loader=yaml.FullLoader)

for key in seed_data:
    valid_line_card.append(key)
print("\n List of valid line cards \n")
print(valid_line_card)
print("\n")

conn = ConnectHandler(device_type=PLATFORM, ip=HOST, port=PORT_SSH, username=USER, password=PASS)
prompt = conn.find_prompt()

version_output = conn.send_command("show version")
version_data = version_output.split("\n")
for line in version_data:
    if "ASR9" in line:
        platform_type = "ASR9000"

print(" Platform kind is \n")
print(platform_type)
print("\n")
        
platform_output = conn.send_command("show platform")
platform_data = platform_output.split("\n")
for line_card in platform_data:
    lc_type = lc_type_pattern.search(line_card)
    if lc_type:
        if lc_type.group() in valid_line_card:
            platform_list.append(line_card.strip().split())
print(" List of valid line cards installed in the chassis \n")
print(platform_list)
print("\n")

interface_output = conn.send_command("show interface brief")
interface_data = interface_output.split("\n")
for interface in interface_data:
     if interface_pattern.search(interface.strip()) and subint_pattern.search(interface.strip()):
        interface_status = interface.strip().split()
        if interface_status[1] =="admin-down" and interface_status[2] == "admin-down":
             interface_list.append(interface_status[:3])
        elif interface_status[1] =="down" and interface_status[2] == "down":
             interface_list.append(interface_status[:3])
print(" List of all physical interfaces in admin-down or down state \n")             
print(interface_list)
print("\n")

for lc in platform_list:
    lc_number = lc_int_number_pattern.search(lc[0])
    for inface in interface_list:
        int_number = lc_int_number_pattern.search(inface[0])
        if int_number.group(1) == lc_number.group(1):
            final_interface_list.append(inface)    
print("\n List of physical interfaces on valid line cards in admin-down or down state \n")
print(final_interface_list)

slice_output = conn.send_command("show platform slices")
slice_data = slice_output.split("\n")
for slice in slice_data:
    if "Power" in slice and "on" in slice:
        slice_list.append(slice.strip().split())
for item in slice_list:
    if "CPU" in item[0] and item[0] not in card_list:
        card_num = item[0]
        card_list.append(item[0])
        slice_struct_data.append(item)
    else:
        item.insert(0, card_num)
        slice_struct_data.append(item)
print("\n Slice list \n")        
print(slice_struct_data)