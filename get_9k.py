"""
ASR9000 specific module to get admin-down and down interfaces from the platform

__copyright__ = "Copyright (c) 2018-2020 aorel, stoporko, vfilippo, vzhovtan@Cisco Systems. All rights reserved."
__author__ = 'vzhovtan'
"""

import re

def interface_list_creation_9k(connection, platform_list):
    #taking 'show interface brief' and selecting interfaces in admin-down and down state on valid line cards only
    interface_pattern = re.compile("Gi\d{1,2}\/.*|TE.*|Hu.*|Fo.*")
    subint_pattern = re.compile(".*ARPA.*")
    lc_int_number_pattern = re.compile("(\d\/\d).*")
    initial_interface_list = []
    final_interface_list = []

    interface_output = connection.send_command("show interface brief")
    interface_data = interface_output.split("\n")
    for interface in interface_data:
        if interface_pattern.search(interface.strip()) and subint_pattern.search(interface.strip()):
            interface_status = interface.strip().split()
            if interface_status[1] =="admin-down" and interface_status[2] == "admin-down":
                initial_interface_list.append(interface_status[:3])
            elif interface_status[1] =="down" and interface_status[2] == "down":
                initial_interface_list.append(interface_status[:3])

    for lc in platform_list:
        lc_number = lc_int_number_pattern.search(lc[0])
        for interface in initial_interface_list:
            int_number = lc_int_number_pattern.search(interface[0])
            if int_number.group(1) == lc_number.group(1):
                final_interface_list.append(interface)
    
    return final_interface_list

def platform_list_creation_9k(connection, valid_line_card):
    #taking 'show platform' output from asr9k and selecting valid line cards only
    lc_type_pattern = re.compile("(A9.+?-[^ \t\r\n\f].*GE)|(A9.+?-MOD.*-)")
    platform_list = []

    platform_output = connection.send_command("show platform")
    platform_data = platform_output.split("\n")
    for line_card in platform_data:
        lc_type = lc_type_pattern.search(line_card)
        if lc_type:
            if lc_type.group() in valid_line_card:
               platform_list.append(line_card.strip().split())

    return platform_list

def slice_list_creation_9k(connection):
    #taking 'show platform slice' from asr9k and returing structured output for all slices
    slice_list = []
    card_list = []
    slice_struct_data = []
    
    slice_output = connection.send_command("show platform slices")
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
        
    return slice_struct_data