import textfsm
import pandas as pd

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
    with open('./static/MAC_OUI.csv', 'r', encoding='utf-8') as mac_f:
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
    vlan_table = {'name' : 'VLANs', 'headers': host['sh_vlan']['headers'], 'data': host['sh_vlan']['results'], 'style':'Table Style Medium 7'}
    return vlan_table

def create_host_vendor_catalogue_table(host):
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
    combined_vlan_table = {'name':'VLANs', 'headers':['VLAN', 'VLAN_NAME'], 'data':[], 'style':'Table Style Medium 7'}
    vlans = set()
    for vlan_table in vlan_tables:
        current_table_headers = vlan_table['headers']
        vlan_id_index = current_table_headers.index('VLAN')
        vlan_name_index = current_table_headers.index('VLAN_NAME')
        vlan_data = vlan_table['data']
        for row in vlan_data:
            current_vlan = row[vlan_id_index]
            current_vlan_name = row[vlan_name_index]
            if not current_vlan in vlans:
                vlans.add(current_vlan)
                combined_vlan_table['data'].append([current_vlan, current_vlan_name])
    return combined_vlan_table