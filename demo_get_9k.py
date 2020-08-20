import re

def interface_list_creation_9k(connection, platform_list):
    #taking 'show interface brief' and selecting interfaces in admin-down and down state on valid line cards only
    interface_pattern = re.compile("Gi\d{1,2}\/.*|Te.*|Hu.*|Fo.*")
    subint_pattern = re.compile(".*ARPA.*")
    lc_int_number_pattern = re.compile("(\d\/\d).*")
    initial_interface_list = []
    final_interface_list = []

    interface_output = connection.send_command("show interface brief")
    interface_data = interface_output.split("\n")
    for interface in interface_data:
        if interface_pattern.search(interface.strip()) and subint_pattern.search(interface.strip()):
            interface_status = interface.strip().split()
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