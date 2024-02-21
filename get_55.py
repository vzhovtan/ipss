"""
NCS5500 specific module to get admin-down and down interfaces from the platform

__copyright__ = "Copyright (c) 2018-2020 aorel, stoporko, vfilippo, vzhovtan@Cisco Systems. All rights reserved."
__author__ = 'vzhovtan'
"""

import re

def platform_list_creation_55(connection):
    #taking 'show platform' output from ncs55k and selecting valid line cards and slices
    platform_list = []
    platform_output = connection.send_command("show platform")
    platform_data = platform_output.split("\n")
    for line_card in platform_data:
        if "Slice" in line_card or "IOS XR RUN" in line_card:
            platform_list.append(line_card.split())
    
    return platform_list

def interface_list_creation_55(connection):
    #taking 'show interface brief' and selecting interfaces in admin-down and down state
    interface_pattern = re.compile("Gi\d{1,2}\/.*|TE.*|Hu.*|Fo.*")
    subint_pattern = re.compile(".*ARPA.*")
    interface_list = []
    interface_output = connection.send_command("show interface brief")
    interface_data = interface_output.split("\n")
    for interface in interface_data:
        if interface_pattern.search(interface.strip()) and subint_pattern.search(interface.strip()):
            interface_status = interface.strip().split()
            if interface_status[1] =="admin-down" and interface_status[2] == "admin-down":
                interface_list.append(interface_status[:3])
            elif interface_status[1] =="down" and interface_status[2] == "down":
                interface_list.append(interface_status[:3])

    return interface_list        