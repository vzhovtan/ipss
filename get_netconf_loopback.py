import re
import xmltodict
from ncclient import manager

loopback_filter = """
    <filter>
      <interfaces xmlns="http://openconfig.net/yang/interfaces">
        <interface>
          <name>Loopback0</name>
          <state/>
        </interface>
      </interfaces>
    </filter>
"""

with manager.connect(
    host='ipv4',
    port=830,
    username='user',
    password='pswd',
    hostkey_verify=False,
    device_params={'name':'iosxr'}
) as m:
    # taking capabilities
    for capability in m.server_capabilities:
        print(capability)

    # test function by getting looback0 interface
    loopback_status = m.get(loopback_filter).data_xml
    print(loopback_status)






