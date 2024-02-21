"""
Gathering data from devices using NetConf and nccclinet library from ASR9000 platforms only

__copyright__ = "Copyright (c) 2018-2020 aorel, stoporko, vfilippo, vzhovtan@Cisco Systems. All rights reserved."
__author__ = 'vzhovtan'
"""

import os
import re
import xmltodict
from ncclient import manager

interface_filter = """
    <filter>
      <interfaces xmlns="http://openconfig.net/yang/interfaces">
        <interface>
          <name/>
            <state>
                <admin-status/>
                <oper-status/>
            </state>
        </interface>
      </interfaces>
    </filter>
"""

platform_filter = """
    <filter>
        <platform xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-plat-chas-invmgr-oper">
            <racks>
                <rack/>
                    <slots>
                        <slot>
                            <instances>
                                <instance>
                                    <state/>
                                </instance>
                            </instances>
                        </slot>
                    </slots>    
            </racks>
        </platform>
    </filter>
"""

user = os.getenv("USER")
pswd = os.getenv("PASSWORD")

with manager.connect(
    host='ipv4',
    port=830,
    username='user',
    password='pswd',
    hostkey_verify=False,
    device_params={'name':'iosxr'}
) as m:
    # capturing server's capabilities
    server_capabilities = []
    for capability in m.server_capabilities:
        server_capabilities.append(capability)

    # capturing admin and oper status for all interface for further processing
    pattern = re.compile("GigabitEthernet\d{1,2}\/|TenGigE\d{1,2\/|HundredGigE")
    interface_raw_data = m.get(interface_filter).data_xml
    interface_dict = {}
    interface_struct_data = (xmltodict.parse(interface_raw_data))["data"]["interfaces"]["interface"]
    for item in interface_struct_data:
        interface_name = item["name"]
        if pattern.match(interface_name):
            interface_state = item.get("state")
            if interface_state:
                interface_dict[interface_name] = interface_state
    print(interface_dict)

    # capturing card type and state for all line cards for further processing
    # returns dictionary of line cards with all needed data for A9K
    platform_status = m.get(platform_filter).data_xml
    line_card_dict = {}
    platform_dict = (xmltodict.parse(platform_status))["data"]["platform"]["racks"]["rack"]["slots"]["slot"]
    for line_card in platform_dict:
        if not isinstance(line_card["instances"]["instance"], list):
            slot_number = line_card["slot-name"]
            line_card_data= dict(line_card["instances"]["instance"]["state"])
            line_card_dict[slot_number] = line_card_data
    print(line_card_dict)




