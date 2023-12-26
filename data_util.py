import os
import re
import data_structures

def extract_oui(mac:str) -> str:
    dividers = [':','-','.']
    mac_without_divider = ''
    for symbol in dividers:
        if symbol in mac:
            mac_without_divider = mac.replace(symbol,'')
    if mac_without_divider == '':
        mac_without_divider = mac
    return mac_without_divider[:6]

def get_vlan_from_port_info(port_info:str) -> str:
    if 'vlan' in port_info:
        vlan_id = port_info[4:]
    else:
        vlan_id = 'na'
    return vlan_id

def convert_subnet_mask_to_subnet_length(subnet_mask:str) -> str:
    '''
    Given a subnet mask like 255.0.0.0 turn it into a subnet length ranging from 0 to 32.
    '''
    subnet_mask_to_length = {
        '0' : 0,
        '128' : 1,
        '192' : 2,
        '224' : 3,
        '240' : 4,
        '248' : 5,
        '252' : 6,
        '254' : 7,
        '255' : 8
    }

    subnet_sections = subnet_mask.split('.')
    if len(subnet_sections) != 4:
        raise ValueError('Subnet must be in the form x.x.x.x')
    
    subnet_length = 0
    for section in subnet_sections:
        if not section in subnet_mask_to_length:
            raise ValueError('Invalid octect value for subnet mask.')
        subnet_length += subnet_mask_to_length[section]
    
    return str(subnet_length)

def process_trunks(os_name:str, interface_details:list[list[str]]) -> list[list[str]]:
    '''
    Takes a table of interfaces and extracts the trunking (LACP) information. Returns
    a table with the trunk interfaces as entries in the interface table.
    '''
    if os_name == 'aos-s':
        table_with_trunk_ints = [interface_details[0],[]]
        trunk_membership_mappings = {}
        trunks = []
        if len(interface_details) == 0:
            raise ValueError('Empty interface details table passed to process_trunks')
        for interface in interface_details[1]:
            trunk_info = interface[-1]
            if trunk_info != '':
                if ' ' in trunk_info:
                    trunk_int, lacp_mode = trunk_info.split(' ')
                else:
                    trunk_int = trunk_info
                    lacp_mode = ''
                if trunk_int in trunk_membership_mappings:
                    trunk_membership_mappings[trunk_int].append(interface)
                else:
                    trunk_membership_mappings[trunk_int] = [interface]
            elif 'trk' in interface[0].lower():
                trunks.append(interface)
            else:
                table_with_trunk_ints[1].append(interface)
        for trunk_int in trunks:
            table_with_trunk_ints[1].append(trunk_int)
            trunk_name = trunk_int[0].lower()
            for member_int in trunk_membership_mappings[trunk_name]:
                table_with_trunk_ints[1].append(member_int)
        return table_with_trunk_ints

def remove_trunk_from_port_name(interface_status_table:list[list[str]]) -> list[list[str]]:
    '''
    Ports that are part of trunks (LACP) have the trunk appended to their names. This function removes the
    trunk portion and returns just the port name. All other information is preserved and passed back.
    '''
    interfaces = interface_status_table[1]
    for interface in interfaces:
        old_name = interface[0]
        new_name = ''
        if '-Trk' in old_name:
            new_name, _ = old_name.split('-')
            interface[0] = new_name
    return interface_status_table

def remove_trunk_from_port_name(interface_status_table:list[list[str]]) -> list[list[str]]:
    '''
    Ports that are part of trunks (LACP) have the trunk appended to their names. This function removes the
    trunk portion and returns just the port name. All other information is preserved and passed back.
    '''
    interfaces = interface_status_table[1]
    for interface in interfaces:
        old_name = interface[0]
        new_name = ''
        if '-Trk' in old_name:
            new_name, _ = old_name.split('-')
            interface[0] = new_name
    return interface_status_table

def update_new_header_indices(parsed_data_header:list[str], new_headers:dict[str,str]):
    '''
    Find and update the new_header indices using the parsed_data_header. If the new_header name does not
    correspond to anything in the parsed_data_header list, panic and exit.
    '''
    try:
        for new_header in new_headers:
            new_headers[new_header]['index'] = parsed_data_header.index(new_header)
    except Exception as e:
        print('Could not find one of the entries in new_header in the parsed_data_header list. All entries in the new_header dict must be present in the parsed_data_header list.')

def add_new_headers_to_parsed_data(existing_datastructure:dict[str,str],parsed_data_info:list[list[str]], new_headers:dict[str,str], matched_parameter_index:int):
    '''
    Add new data to entries in the parsed_data list of entries. Entries are added based on the matched_parameter_index
    which is the value that must be similar across different parsed datastructures. Throws an error if there is no match
    for a key in the parsed_data_info.
    '''
    for new_header in new_headers:
        new_header_name = new_headers[new_header]['new_name']
        existing_datastructure['headers'].append(new_header_name)
    for item in parsed_data_info:
        item_name = item[matched_parameter_index]
        if item_name in existing_datastructure['data']:
            for new_header in new_headers:
                new_header_name = new_headers[new_header]['new_name']
                header_index = new_headers[new_header]['index']
                existing_datastructure['data'][item_name][new_header_name] = item[header_index]
        else:
            print(f'Could not find {item_name} in original table, skipping {item_name}...')
    
def fill_data_with_empty_values(existing_datastructure:dict[str,str], new_headers:dict[str,str]):
    '''
    Used after the add_new_headers_to_parsed_data function. Fills in empty values for items that did not
    have a corresponding entry.
    '''
    total_headers = len(existing_datastructure['headers'])
    for _,item_info in existing_datastructure['data'].items():
        num_entries_in_item = len(item_info.keys())
        if total_headers-1 != num_entries_in_item:
            for new_header in new_headers:
                new_header_name = new_headers[new_header]['new_name']
                item_info[new_header_name] = ''

def convert_dictionary_to_table_structure(existing_datastructure:dict[str,str], match_key:str='') -> list[list[str]]:
    '''
    Converts the dictionary of items into a list of list of items appropriate for the pandas.to_excel method to
    write the information to an excel table.
    '''
    table = []
    ds_dict_data = existing_datastructure['data'] 
    ds_headers = existing_datastructure['headers']
    for key,item_data in ds_dict_data.items():
        current_item = []
        if len(ds_headers) > 1:
            for header in ds_headers:
                if not header == match_key:
                    current_item.append(item_data[header])
                else:
                    current_item.append(key)
        else:
            current_item.append(key)
        table.append(current_item)
    return table

def create_outputs_ds(device_info:list[list[str]], parsed_data_to_add:list) -> dict:
    '''
    device_info is a list of textFSM extracted parsed data.
    parsed_data_to_add is a list of dictionaries that are formatted as:
        {
            'table_name' : Name of the table to add. Must correspond to the template file with parsed info.,
            'headers_to_add' : a list of TUPLES (old_header_name, new_header_name),
            'table_index' : index of table in device_info
        }
    Returns:
        {
            'table_name' : {
                'parsed_data' : taken from the device_info list,
                'new_headers' : {
                    'old_header_name' : {
                        'index' : 0,
                        'new_name' : new_header_name
                    }...
                }
            }
        }
    '''
    outputs = {}
    if len(parsed_data_to_add) == 0:
        return outputs
    for table_to_add in parsed_data_to_add:
        table_name = table_to_add['table_name']
        outputs[table_name] = {}
        table_headers = table_to_add['headers_to_add']
        table_index = table_to_add['table_index']
        outputs[table_name]['parsed_data'] = device_info[table_index]
        for old_header, new_header in table_headers:
            if not 'new_headers' in outputs[table_name].keys():
                outputs[table_name]['new_headers'] = {}
                outputs[table_name]['new_headers'][old_header] = {'index':0, 'new_name':new_header}
            else:
                outputs[table_name]['new_headers'][old_header] = {'index':0, 'new_name':new_header}
    return outputs

def create_excel_printable_table(name:str, data:dict, headers:list[str], convert_table:bool=True) -> dict:
    '''
    Return a dictionary of the form: 
    {
        'name' : name,
        'headers' : headers,
        'data' : [
        [...]
        ]
    }
    '''
    table = {
        'name' : name,
        'headers' : headers,
        'data' : data
    }
    if convert_table:
        data_converted_into_table = convert_dictionary_to_table_structure(table)
        table['data'] = data_converted_into_table
    return table

def extract_hostname_from_cli_output(cli_output:list[str]) -> str:
    '''
    Given a list of CLI output, attempt to extract the hostname from the output. Note that this information
    only exists if the file was logged from a putty or similar manual session.
    '''
    show_command_line = re.compile(r'.*# *sho?w?')
    for line in cli_output:
        if show_command_line.match(line) is not None:
            hostname, _ = line.split('#')
            return hostname
    return ''

def convert_vlan_ip_subnet_to_slash_notation(vlan_info:list[list[str]]) -> list[str]:
    '''
    Converts the VLAN IP_ADDRESS and SUBNET mask into an IP_ADDRESS/MASK format where
    mask is a two digit number.
    '''
    vlan_headers = vlan_info[0]
    vlan_data = vlan_info[1]
    ip_address_index = vlan_headers.index('IP_ADDRESS')
    ip_subnet_index = vlan_headers.index('SUBNET')
    vlan_id_index = vlan_headers.index('VLAN_ID')
    ip_address_subnet = [['VLAN_ID', 'IP_ADDRESS'],[]]
    for vlan in vlan_data:
        vlan_id = vlan[vlan_id_index]
        vlan_ip_address = vlan[ip_address_index]
        if vlan_ip_address == '':
            ip_address_subnet[1].append([vlan_id, ''])
        else:
            vlan_subnet_mask = vlan[ip_subnet_index]
            vlan_subnet_length = convert_subnet_mask_to_subnet_length(vlan_subnet_mask)
            ip_address_subnet[1].append([vlan_id, vlan_ip_address + '/' + vlan_subnet_length])
    return ip_address_subnet

def os_has_no_data_in_tables(tables:dict, os_name:str) -> bool:
    '''
    Returns true if the key entry os_name in the tables dictionary is an empty list.
    '''
    return len(tables[os_name]) == 0

def extract_device_info_from_sh_mac_address(sh_mac_output:list[list[str]], sh_mac_headers:list[str]) -> dict[dict[str, str]]:
    devices = {} 
    mac_index = sh_mac_headers.index('MAC')
    vlan_index = sh_mac_headers.index('VLAN')
    port_index = sh_mac_headers.index('PORT')
    for line in sh_mac_output:
        current_device = {}
        current_device_mac = line[mac_index]
        current_device['vlan'] = line[vlan_index]
        current_device['physical_port'] = line[port_index]
        devices[current_device_mac] = current_device
    return devices

def add_ip_information_to_devices(arp_info:list[list[str]], arp_info_headers:list[str], devices:dict[dict[str, str]]) -> None:
    mac_index = arp_info_headers.index('MAC')
    ip_index = arp_info_headers.index('IP')
    for arp_entry in arp_info:
        current_mac = arp_entry[mac_index]
        current_ip = arp_entry[ip_index]
        if current_mac in devices:
            devices[current_mac]['ip'] = current_ip

def add_mac_oui_to_devices(devices:dict[dict[str,str]]) -> None:
    for mac in devices:
        mac_oui = extract_oui(mac)
        devices[mac]['mac_oui'] = mac_oui

def add_mac_vendor_to_devices(devices:dict[dict[str,str]], mac_vendors:dict[str, str]) -> None:
    for mac in devices:
        mac_oui = devices[mac]['mac_oui']
        if mac_oui in mac_vendors:
            devices[mac]['mac_vendor'] = mac_vendors[mac_oui]
        else:
            devices[mac]['mac_vendor'] = 'na'

def catalogue_devices_by_vendor(devices:dict[dict[str,str]]) -> dict[str, int]:
    catalogue = {}
    for mac in devices:
        vendor_name = devices[mac]['mac_vendor']
        if vendor_name not in catalogue:
            catalogue[vendor_name] = 1
        else:
            catalogue[vendor_name] += 1
    return catalogue

def create_mac_vendors_dict_from_mac_oui_csv() -> dict[str, str]:
    '''
    Uses the MAC_OUI.csv file found in the static folder to create a dictionary of MAC OUI to vendor information.
    '''
    mac_oui_csv = './static/MAC_OUI.csv'
    if not os.path.exists(mac_oui_csv):
        raise FileNotFoundError('The MAC_OUI.csv file is not found in the static folder. This CSV file is required for this script to work.')
    with open(mac_oui_csv, 'r', encoding='utf-8') as mac_f:
        mac_vendors = {}
        lines = mac_f.readlines()
        for line in lines[1:]:
            oui = line[:6].lower()
            company = line[7:].replace('\n','')
            mac_vendors[oui] = company
    return mac_vendors 

def add_information_to_devices_from_tables(device_tables:list[list[str]], mac_vendors:dict[str,str]) -> dict[str,dict[str,str]]:
    '''
    Creates a dictionary of MAC to device details. The details are taken from the extracted tables passed in the table_results parameter.
    This table should have three tables: the sh_mac_address, sh_vlan and sh_arp tables.
    '''
    devices = extract_device_info_from_sh_mac_address(device_tables['sh_mac_address']['results'], device_tables['sh_mac_address']['headers'])
    if 'sh_arp' in device_tables:
        add_ip_information_to_devices(device_tables['sh_arp']['results'], device_tables['sh_arp']['headers'],devices)
    add_mac_oui_to_devices(devices)
    add_mac_vendor_to_devices(devices, mac_vendors)
    return devices

def create_host_main_table(host_devices:dict[str,dict[str,str]], host_name:str='HOST') -> dict:
    '''
    Creates the dictionary that has three keys:
    1. name: hostname of the device from which all information was extracted.
    2. headers: the headers of this table which contains the following:
      MAC OUI 
      MAC ADDRESS
      IP Address
      MAC Vendor
      Port
      VLAN
      Notes
      Auth Type
      CP Role
      Role
      Enforcement Profile
    3. data: the rows of the table.
    The host_name is an optional parameter for the name of the host
    '''
    main_mac_table = {'name': host_name}
    headers = ['MAC OUI', 'MAC Address', 'IP Address', 'MAC Vendor', 'Port', 'VLAN', 'Notes', 'Auth Type', 'CP Role', 'Role', 'Enforcement Profile']
    devices_list = []
    for mac in host_devices:
        ip_address = ''
        if 'ip' in host_devices[mac]:
            ip_address = host_devices[mac]['ip']
        devices_list.append([host_devices[mac]['mac_oui'], mac, ip_address, host_devices[mac]['mac_vendor'], host_devices[mac]['physical_port'], host_devices[mac]['vlan'], '', '', '', '', ''])
    main_mac_table['headers'] = headers
    main_mac_table['data'] = devices_list
    return main_mac_table


def create_host_vendor_catalogue_table(host_devices:dict[str, dict[str,str]]) -> dict:
    '''
    Creates a table of Vendor Name to number of devices in the network that comes from that vendor.
    '''
    vendor_catalogue_table = {'name':'Number of devices by Vendor.'}
    vendor_catalogue = catalogue_devices_by_vendor(host_devices)
    vc_list = []
    for vendor in vendor_catalogue:
        vc_list.append([vendor, vendor_catalogue[vendor]])
    vc_headers = ['Vendor', 'Count']
    vendor_catalogue_table['headers'] = vc_headers
    vendor_catalogue_table['data'] = vc_list
    vendor_catalogue_table['style'] = 'Table Style Medium 6'
    return vendor_catalogue_table

def combine_vendor_catalogue_tables(vendor_catalogue_tables) -> dict:
    '''
    Creates a table that combines all vendor:count information across multiple hosts.
    The final table contains all vendor to number of devices from the vendor across all host files computed.
    '''
    combined_vc_table = {'name' : 'Number of devices by Vendor'}
    combined_list = {}
    for vc_table in vendor_catalogue_tables:
        current_vc_data = vc_table['data']
        for vendor,count in current_vc_data:
            if vendor in combined_list:
                combined_list[vendor] += count
            else:
                combined_list[vendor] = count
    combined_vc_table['data'] = [[vendor, count] for vendor,count in combined_list.items()]
    combined_vc_table['style'] = 'Table Style Medium 6'
    combined_vc_table['headers'] = ['Vendor', 'Count']
    return combined_vc_table

def create_host_main_mac_tables(host):
    '''
    Creates the main MAC table for the host that is passed to the function.
    The created table has the following headers: 
    MAC OUT, MAC Address, IP Address, MAC Vendor, Port, VLAN, Notes, Auth Type, CP Role, Role and Enforcement Profile
    '''
    main_mac_table = {'name': host['hostname']}
    headers = ['MAC OUI', 'MAC Address', 'IP Address', 'MAC Vendor', 'Port', 'VLAN', 'Notes', 'Auth Type', 'CP Role', 'Role', 'Enforcement Profile']
    devices_list = []
    devices = host['devices']
    for mac in devices:
        ip_address = ''
        if 'ip' in devices[mac]:
            ip_address = devices[mac]['ip']
        devices_list.append([devices[mac]['mac_oui'], mac, ip_address, devices[mac]['mac_vendor'], devices[mac]['physical_port'], devices[mac]['vlan'], '', '', '', '', ''])
    main_mac_table['headers'] = headers
    main_mac_table['data'] = devices_list
    return main_mac_table

def create_host_vlan_table_from_sh_mac_address_info(host):
    '''
    If the show vlan command was not part of the configuration output, VLAN information will be extracted from the
    show mac-address table. The only information missing would be the VLAN names, which are populated to be
    VLAN{VLAN_ID}. For example vlan 20 would have the name VLAN20.
    The returned table has the following headers:
    VLAN, VLAN_NAME, HEX and DECIMAL
    '''
    vlan_table = {'name': 'VLANs', 'headers':['VLAN', 'VLAN_NAME', 'HEX', 'DECIMAL'], 'data':[], 'style':'Table Style Medium 7'}
    devices = host['devices']
    vlans = set()
    for mac in devices:
        vlan = devices[mac]['vlan']
        if not vlan in vlans:
            vlans.add(vlan)
            vlan_name = 'VLAN'+vlan
            vlan_hex = str(hex(int(vlan)))
            vlan_decimal = ''
            vlan_table['data'].append([vlan, vlan_name, vlan_hex, vlan_decimal])
    return vlan_table

def create_host_vlan_table(host):
    '''
    Returns a table with VLAN information for the host that is passed to the function. The VLAN ID and name removed from the results section
    of the sh_vlan key. The hex and decimal values are then added in place of all other VLAN information.
    The returned table has the following headers:
    VLAN, VLAN_NAME, HEX and DECIMAL
    '''
    vlan_table_headers = ['VLAN', 'VLAN_NAME', 'HEX', 'DECIMAL']
    sh_vlan_headers = host['sh_vlan']['headers']
    sh_vlan_data = host['sh_vlan']['results']
    vlan_index = sh_vlan_headers.index('VLAN')
    vlan_name_index = sh_vlan_headers.index('VLAN_NAME')
    vlan_table_data = []
    for row in sh_vlan_data:
        vlan = row[vlan_index]
        vlan_name = row[vlan_name_index]
        vlan_hex = str(hex(int(vlan)))
        vlan_decimal = ''
        vlan_table_data.append([vlan, vlan_name, vlan_hex, vlan_decimal])
    vlan_table = {'name':'VLANs', 'headers':vlan_table_headers, 'data':vlan_table_data, 'style':'Table Style Medium 7'}
    return vlan_table

def create_host_vendor_catalogue_table(host):
    '''
    Returns a table cataloging the vendors and number of devices that belongs to that vendor.
    The returned table has the following headers:
    Vendor and Count
    '''
    vendor_catalogue_table = {'name':'Number of devices by Vendor.'}
    vendor_catalogue = catalogue_devices_by_vendor(host['devices'])
    vc_list = []
    for vendor in vendor_catalogue:
        vc_list.append([vendor, vendor_catalogue[vendor]])
    vc_headers = ['Vendor', 'Count']
    vendor_catalogue_table['headers'] = vc_headers
    vendor_catalogue_table['data'] = vc_list
    vendor_catalogue_table['style'] = 'Table Style Medium 6'
    return vendor_catalogue_table

def combine_vlan_tables(vlan_tables):
    '''
    Combines all VLAN table information into one VLAN table.
    '''
    combined_vlan_table = {'name':'VLANs', 'headers':['VLAN', 'VLAN_NAME', 'HEX', 'DECIMAL'], 'data':[], 'style':'Table Style Medium 7'}
    vlans = set()
    for vlan_table in vlan_tables:
        vlan_data = vlan_table['data']
        for row in vlan_data:
            current_vlan = row[0]
            if not current_vlan in vlans:
                vlans.add(current_vlan)
                combined_vlan_table['data'].append(row)
    return combined_vlan_table

def merge_tables_into_one_table(tables:list[list[str]]) -> list[list[str]]:
    '''
    Merges a set of tables that have similar headers into one table. Returns
    the merged table.
    '''
    merged_table = []
    all_table_headers = []
    for table in tables:
        table_headers = table[0]
        for header in table_headers:
            if not header in all_table_headers:
                all_table_headers.append(header)
    for table in tables:
        table_contents = table[1]
        table_headers = table[0]
        for row in table_contents:
            new_row = ['' for _ in all_table_headers]
            for header,item in zip(table_headers,row):
                item_index = all_table_headers.index(header)
                new_row[item_index] = item
            merged_table.append(new_row)
    return (all_table_headers, merged_table)    

def reorder_table_based_on_new_header_order(orig_table:list[list[str]], new_headers:list[str]):
    '''
    Returns a table in the order outlined in new_headers. If new_headers contain headers not in the
    original table, fill that column in each row with an empty string.
    '''
    orig_headers = orig_table[0]
    orig_data = orig_table[1]
    new_data = []
    orig_index = {}
    for new_header in new_headers:
        if new_header in orig_headers:
            orig_index[new_header] = orig_headers.index(new_header)
        else:
            orig_index[new_header] = -1
    for orig_row in orig_data:
        new_row = []
        for new_header in new_headers:
            new_header_index = orig_index[new_header]
            if new_header_index == -1:
                new_row.append('')
            else:
                new_row.append(orig_row[new_header_index])
        new_data.append(new_row)
    new_table = [new_headers, new_data]
    return new_table

def create_base_table(base_data:list[list[str]], headers_to_include:list[str], main_key:str, base_table:dict):
    '''
    The base_data is a list of two lists:
        headers_list is the first item. A list of strings representing the headers of the table.
        data_list is a list of lists, each list representing a row of data.
    The headers_to_include is a subset of the headers from which to build the base table from the data.
    main_key is a string
    base_table is a dictionary where the base_table data will be included.
    '''
    base_headers = base_data[0]
    base_rows = base_data[1]
    for row in base_rows:
        current_data = {}
        for header,attribute in zip(base_headers, row):
            if header == main_key:
                base_table[attribute] = current_data
            elif header in headers_to_include:
                current_data[header] = attribute
    return_table = {}
    return_table['headers'] = headers_to_include
    return_table['data'] = base_table
    return return_table

def add_new_info_from_other_tables_to_table(table:dict, new_outputs:dict,matched_parameter_index:int=0):
    '''
    The table is of the type:
        {
            'headers' : list[str],
            'data' : dict[str, str]
        }
    The new_outputs is of the type:
        {
            NAME : {
                'parsed_data' : [
                    list[str],
                    [
                        list[str]
                    ]
                ],
                'new_headers' : {
                    OLD_HEADER_NAME : 
                        'index' : 0,
                        'new_name' : NEW_HEADER_NAME`
                }
            }
        }
    NAME is an arbitrary string separating each table with information to add to the table.
    '''
    for _,output_data in new_outputs.items():
        output_headers = output_data['parsed_data'][0]
        output_info = output_data['parsed_data'][1]
        output_new_headers = output_data['new_headers']
        update_new_header_indices(output_headers, output_new_headers)
        add_new_headers_to_parsed_data(table, output_info, output_new_headers, matched_parameter_index)
        fill_data_with_empty_values(table, output_new_headers)

def create_column_ds(col_tables:list[dict], ds:list[list[str]]) -> list[list[str]]:
    '''
    Creates excel printable tables encoded in col_tables list.
    ds is a list of parsed information presented in tables that textFSM produces.
    '''
    column = []
    for table in col_tables:
        base_table_index = table['base_table']['base_table_index']
        base_table_headers = table['base_table']['headers_to_include']
        base_table_key = table['base_table']['key']
        base_table = create_base_table(ds[base_table_index], base_table_headers, base_table_key, {})
        if 'parsed_info_to_add' in table:
            parsed_info_to_add = table['parsed_info_to_add']
            if len(parsed_info_to_add) > 0:
                outputs = create_outputs_ds(ds, parsed_info_to_add)
                matched_parameter_index = 0
                if 'matched_parameter_index' in table:
                    matched_parameter_index = table['matched_parameter_index']
                add_new_info_from_other_tables_to_table(base_table, outputs, matched_parameter_index)
        table_name = table['table_name']
        table_final_headers = table['final_headers']
        current_headers = base_table['headers']
        convert_table = table['convert_table']
        if convert_table:
            converted_table = convert_dictionary_to_table_structure(base_table, base_table_key)
            base_table['data'] = converted_table
            convert_table = False
        if current_headers != table_final_headers:
            base_table = reorder_table_based_on_new_header_order([current_headers,base_table['data']], table_final_headers)[1]
        else:
            base_table = base_table['data']
        printable_table = create_excel_printable_table(table_name, base_table, table_final_headers, convert_table)
        column.append(printable_table)
    return column

def process_mgmt_int_information(management_int:str, supported_os:str, current_device_info, device, new_row):
    '''
    Adds mgmt information to the systems in the overview systems tab.
    params:
        management_int: A string that indicates either the vlan or interface of the mgmt interface
        supported_os: The OS that the device belongs to.
        current_device_info: The table with system information for the device
        device: A list of tuples with the headers and parsed information for a device.
    '''
    if supported_os == 'aos-cx':
        int_source = ''
        found_vlan = False
        if 'vlan' in management_int:
            int_source = management_int.split(' ')[-1]
            int_vlan_table = device[data_structures.os_templates[supported_os].index('sh_run_int_vlans.template')]
            vlan_table_headers = int_vlan_table[0]
            vlan_table_data = int_vlan_table[1]
            for data_row in vlan_table_data:
                vlan_id_index = vlan_table_headers.index('VLAN_ID')
                if data_row[vlan_id_index] == int_source:
                    mgmt_ip_index = current_device_info[0]['headers'].index('MGMT_IP')
                    mgmt_source_index = current_device_info[0]['headers'].index('MGMT_SOURCE')
                    vlan_ip_index = vlan_table_headers.index('IP_ADDRESS')
                    new_row[mgmt_ip_index] = data_row[vlan_ip_index]
                    new_row[mgmt_source_index] = f'VLAN {int_source}'
                    found_vlan = True
                    break
            if not found_vlan:
                print('management vlan information not found in vlan table, skipping mgmt interface information processing...')
        else:
            int_source = management_int

def truncate_interface_names(table, os:str):
    '''
    Changes the interface names in the cdp_neighbor_table to their truncated versions.
    i.e. GigabitEthernet1/0/1 becomes Gi1/0/1, Port-Channel10 becomes Po10, etc.
    This is required to match how the interface names are presented in other show commands.
    '''

    headers = table[0]
    data = table[1]
    interface_index = headers.index('INTERFACE')

    for data_row in data:
        interface = data_row[interface_index]
        if 'Ethernet' in interface:
            split_int = interface.split('/')
            if os == 'ios-xe':
                prefix = split_int[0][:2] + split_int[0][-1]
                new_int_name = prefix + '/' + split_int[1] + '/' + split_int[2]
            elif os == 'nx-os':
                prefix = 'Eth' + split_int[0][-1]
                new_int_name = prefix + '/' + split_int[1]
            data_row[interface_index] = new_int_name
        elif 'port-channel' in interface.lower():
            num_index = interface.index('l') + 1
            new_int_name = 'Po' + interface[num_index:]
            data_row[interface_index] = new_int_name