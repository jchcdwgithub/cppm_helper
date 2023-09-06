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

def extract_device_info_from_sh_mac_address(sh_mac_output:list[list[str]]) -> dict[dict[str, str]]:
    devices = {} 
    for line in sh_mac_output:
        current_device = {}
        current_device_mac = line[0]
        current_device['vlan'] = line[1]
        current_device['type'] = line[2]
        current_device['physical_port'] = line[3]
        devices[current_device_mac] = current_device
    return devices

def add_ip_information_to_devices(arp_info:list[list[str]], devices:dict[dict[str, str]]) -> None:
    for arp_entry in arp_info:
        current_mac = arp_entry[1]
        current_ip = arp_entry[0]
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
    devices = extract_device_info_from_sh_mac_address(device_tables['sh_mac_address']['results'])
    add_ip_information_to_devices(device_tables['sh_arp']['results'], devices)
    add_mac_oui_to_devices(devices)
    add_mac_vendor_to_devices(devices, mac_vendors)
    return devices

def create_host_main_table(host_devices:dict[str,dict[str,str]], host_name:str='HOST') -> dict:
    '''
    Creates the dictionary that has three keys:
    1. name: hostname of the device from which all information was extracted.
    2. headers: the headers of this table which contains the following:
      MAC OUT 
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

def combine_vendor_catalogue_data(vendor_catalogue_tables) -> dict:
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
    combined_vc_table['style'] = 'Table Sytle Medium 6'
    return combined_vc_table