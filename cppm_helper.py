import textfsm
import pandas as pd

'''
df = pd.read_excel('ANX Switch Build.xlsx', sheet_name='MAC OUI') 
ouis = df[df.columns[0]].values.tolist()
companies = df[df.columns[1]].values.tolist()
with open('./show_files/MAC_OUI.csv', 'w', encoding='utf-8') as f:
    entries = ['oui,company\n']
    for oui,company in zip(ouis,companies):
        entries.append(f'{oui},{company}\n')
    f.writelines(entries)
print('done.')
'''

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

mac_address_template = './templates/sh_mac_address.template' 
arp_template = './templates/sh_arp.template'
output_file = 'mac-arp-table-CX.txt'

with open(mac_address_template) as mac_tf, open(output_file) as of:
    re_mac_table = textfsm.TextFSM(mac_tf)
    sh_mac_address_result = re_mac_table.ParseText(of.read())

with open(arp_template) as arp_tf, open(output_file) as of:
    re_arp_table = textfsm.TextFSM(arp_tf)
    sh_arp_result = re_arp_table.ParseText(of.read())

with open('./show_files/MAC_OUI.csv', 'r', encoding='utf-8') as mac_f:
    mac_vendors = {}
    lines = mac_f.readlines()
    for line in lines[1:]:
        oui = line[:6].lower()
        company = line[7:].replace('\n','')
        mac_vendors[oui] = company 

devices = extract_device_info_from_sh_mac_address(sh_mac_address_result)
add_ip_information_to_devices(sh_arp_result, devices)
add_mac_oui_to_devices(devices)
add_mac_vendor_to_devices(devices, mac_vendors)

print('done.')