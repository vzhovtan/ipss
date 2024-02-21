#!/usr/bin/python3

"""
Python script to be used along with Ansible role

__copyright__ = "Copyright (c) 2018-2020 aorel, stoporko, vfilippo, vzhovtan@Cisco Systems. All rights reserved."
__author__ = 'vzhovtan'
"""

import sys
import json
import re

#define regular expressions
interface_pattern = re.compile("GigabitEthernet\S*|TwentyFiveGigE\S*|TenGigE\S*|FortyGig\S*|HundredGigE\S*")
subint_pattern = re.compile("GigabitEthernet\S*\.|TwentyFiveGigE\S*\.|TenGigE\S*\.|FortyGig\S*\.|HundredGigE\S*\.")
lc_number_pattern = re.compile("(\d\/\d).*")
int_number_pattern = re.compile("[a-zA-Z].?(\d\/\d).*")

def get_hostname(worklist):
    #looks for the hostname
    for line in worklist:
        if "hostname" in line.lower():
            result = line.replace("hostname ", "")
    return  result       

def get_sdr(worklist):
    #look for show sdr in 64-bit XR and extract relevant line cards informaiton
    sdr_list = []
    for line_card in worklist:
        if "ios xr run" in line_card.lower():
            if "rp" not in line_card.lower():
                lc_entry = line_card.strip().split()
                if lc_entry:
                    lc_location = lc_entry[1]
                    sdr_list.append(lc_location)
    return sdr_list

def get_interface(int_list, sdr_list):
    #look for show ipv4 vrf all int brief and find physical interfaces on the selected line card
    initial_interface_list = []
    final_interface_list = []
    for interface in int_list:
        if interface_pattern.search(interface.strip()):
            if not subint_pattern.search(interface.strip()):
                interface_status = interface.strip().split()
                interface_list_entry = [interface_status[0], interface_status[2], interface_status[3]]
                initial_interface_list.append(interface_list_entry)

    for lc in sdr_list:
        lc_number = lc_number_pattern.search(lc)
        if lc_number:
            for interface in initial_interface_list:
                int_number = int_number_pattern.search(interface[0])
                if int_number:
                    if int_number.group(1) == lc_number.group(1):
                        final_interface_list.append(interface)            
    return final_interface_list

if __name__ == '__main__':
    selected_platform_data = {}
    all_platform_data = {}
    worklist = []

    for item in sys.argv[1:]:
        worklist.append(item)

    nodename = get_hostname(worklist)
    sdr_list = get_sdr(worklist)

    if sdr_list:
        interface_list = get_interface(worklist, sdr_list)
        selected_platform_data["line_cards"] = sdr_list
        selected_platform_data["interfaces"] = interface_list
        all_platform_data[nodename] = selected_platform_data

    with open("outcome.json", "a") as file:
        file.write(json.dumps(all_platform_data))