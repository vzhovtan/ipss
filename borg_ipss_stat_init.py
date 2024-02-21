from __future__ import unicode_literals, absolute_import, print_function
from bdblib.exceptions import BDBTaskError
from task_xr_automation_library import XRSquareWheels4, XRFileExport, XRMetaData
from pymongo import MongoClient
from borg3.result import *
import bdblib
import logging
import json
import re


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def borg_module(env, meta_data):
    """
    inspects an IOS XR showtech and capture data for IPSS calculation.
    """
    valid_line_card = ["A9K-48X10GE-1G", "A9K-4X100GE", "A9K-8X100GE", "A9K-MOD400", "A9K-400GE", \
        "A9K-16X100GE", "A99-48X10GE-1G", "A99-8X100GE", "A99-12X100GE", "A99-32X100GE"]
    lc_type_pattern = re.compile("(A9.+?-MOD.*0)|(A9.+?-48.+?GE.+?G)|(A9.+?-[a-zA-Z0-9].*GE)")
    interface_pattern = re.compile("Gi\S*|Te\S*|Hu\S*|Fo\S*")
    subint_pattern = re.compile("Gi\S*\.|Te\S*\.|Hu\S*\.|Fo\S*\.")
    lc_number_pattern = re.compile("(\d\/\d).*")
    int_number_pattern = re.compile("[a-zA-Z].?(\d\/\d).*")
    selected_platform_data = {}
    all_platform_data = {}

    result_list = ResultList()
    xr_file = meta_data["xr_file"]
    host_name = meta_data["device"].get_hostname()
    platform = meta_data["device"].get_platform()
    if platform and platform == 'ASR9K':
        platform_list = get_platform(xr_file, valid_line_card, lc_type_pattern)
        sdr_list = get_sdr(xr_file, valid_line_card, lc_type_pattern)
        if platform_list:
            interface_list = get_interface(xr_file, platform_list, interface_pattern, subint_pattern, lc_number_pattern, int_number_pattern)
            result_list.debug("platform information below")
            selected_platform_data["line_cards"] = platform_list
            selected_platform_data["interfaces"] = interface_list
            all_platform_data[host_name] = selected_platform_data
            result_list.debug(json.dumps(all_platform_data))
            insert_to_mongoDB(all_platform_data)
        elif sdr_list:
            interface_list = get_interface(xr_file, sdr_list, interface_pattern, subint_pattern, lc_number_pattern, int_number_pattern)
            result_list.debug("sdr information below")
            selected_platform_data["line_cards"] = sdr_list
            selected_platform_data["interfaces"] = interface_list
            all_platform_data[host_name] = selected_platform_data
            result_list.debug(json.dumps(all_platform_data))
            insert_to_mongoDB(all_platform_data)

    result_list.add_result(OkResult(title='The script has completed'))
    return result_list

def get_platform(filename, valid_line_card, lc_type_pattern):
    #Look for the admin show platform in classic XR showtech file
    platform_list = []
    sw = filename.get_xr_square_wheels()
    snippet = sw.get_first_system_command("admin show platform")
    if snippet:
        for line_card in snippet.text.splitlines():
            if "A9" in line_card:
                lc_type = lc_type_pattern.search(line_card)
                if lc_type:
                    if lc_type.group() in valid_line_card:
                        lc_entry = line_card.strip().split()
                        if lc_entry:
                            platform_list_entry = [lc_entry[0], lc_entry[1]]
                            platform_list_entry.append(lc_type.group())
                            platform_list.append(platform_list_entry)

    return platform_list

def get_sdr(filename, valid_line_card, lc_type_pattern):
    #look for show sdr in 64-bit XR show tech file
    sdr_list = []
    sw = filename.get_xr_square_wheels()
    snippet = sw.get_first_system_command("show sdr")
    if snippet:
        for line_card in snippet.text.splitlines():
            if "A9" in line_card:
                lc_type = lc_type_pattern.search(line_card)
                if lc_type:
                    if lc_type.group() in valid_line_card:
                        lc_entry = line_card.strip().split()
                        logging.debug(lc_entry)
                        if lc_entry:
                            lc_location = lc_entry[1] + "/CPU0"
                            sdr_list_entry = [lc_location, lc_entry[0]]
                            sdr_list_entry.append(lc_type.group())
                            sdr_list.append(sdr_list_entry)

    return sdr_list

def get_interface(filename, platform_sdr_list, interface_pattern, subint_pattern, lc_number_pattern, int_number_pattern):
    #look for show ipv4 vrf all int brief in XR show tech file
    initial_interface_list = []
    final_interface_list = []
    sw = filename.get_xr_square_wheels()
    snippet = sw.get_first_system_command("show ipv4 vrf all int brief")
    if snippet:
        for interface in snippet.text.splitlines():
            if interface_pattern.search(interface.strip()):
                if not subint_pattern.search(interface.strip()):
                    interface_status = interface.strip().split()
                    interface_list_entry = [interface_status[0], interface_status[2], interface_status[3]]
                    initial_interface_list.append(interface_list_entry)

        for lc in platform_sdr_list:
            lc_number = lc_number_pattern.search(lc[0])
            if lc_number:
                for interface in initial_interface_list:
                    int_number = int_number_pattern.search(interface[0])
                    if int_number:
                        if int_number.group(1) == lc_number.group(1):
                            final_interface_list.append(interface)            

    return final_interface_list

def insert_to_mongoDB(data):
    client = MongoClient()
    mydb = client["task_ipss_pilot"]
    mycol = mydb["ipss_stats"]
    rl = mycol.insert_one(data) 
