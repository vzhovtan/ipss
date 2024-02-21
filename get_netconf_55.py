"""
Gathering data from devices using NetConf and nccclinet library from NCS5500 platforms only

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
        <platform xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-plat-chas-invmgr-ng-oper">
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
    pattern = re.compile("GigabitEthernet\d{1,2}\/|TenGigE|HundredGigE")
    interface_raw_data = m.get(interface_filter).data_xml
    interface_dict = {}
    interface_struct_data = (xmltodict.parse(interface_raw_data))["data"]["interfaces"]["interface"]
    for item in interface_struct_data:
        interface_name = item["name"]
        if pattern.match(interface_name):
            interface_state = dict(item["state"])
            interface_dict[interface_name] = interface_state
    print(interface_dict)

    # capturing card type and state for all line cards for further processing
    # returns dictionary of slices with admin state for NCS55K
    platform_status = m.get(platform_filter).data_xml
    slice_dict = {}
    platform_dict = (xmltodict.parse(platform_status))["data"]["platform"]["racks"]["rack"]["slots"]["slot"]
    for line_card in platform_dict:
        slice_list = line_card.get("instances")
        if slice_list:
            for slice in slice_list["instance"]:
                slice_number = slice["state"]["node-name"]
                slice_admin_state = slice["state"]["state"]
                slice_dict[slice_number] = slice_admin_state
    print(slice_dict)







