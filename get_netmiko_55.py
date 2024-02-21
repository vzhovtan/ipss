"""
Gathering data from devices using Netmiko library from NCS5500 platforms only

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

interface_list = []
platform_list = []
platform_type = ""

interface_pattern = re.compile("Gi\d{1,2}\/.*|TE.*|Hu.*|Fo.*")
subint_pattern = re.compile(".*ARPA.*")

conn = ConnectHandler(device_type=PLATFORM, ip=HOST, port=PORT_SSH, username=USER, password=PASS)
prompt = conn.find_prompt()

version_output = conn.send_command("show version")
version_data = version_output.split("\n")
for line in version_data:
     if "NCS-5500" in line:
        platform_type = "NCS5500"

print("\n Platform kind is \n")
print(platform_type)
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

platform_output = conn.send_command("show platform")
platform_data = platform_output.split("\n")
for line_card in platform_data:
    if "Slice" in line_card or "IOS XR RUN" in line_card:
        platform_list.append(line_card.split())

print(" List of valid line cards installed in the chassis and slices\n")
print(platform_list)
print("\n")
