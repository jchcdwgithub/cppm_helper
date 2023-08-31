import sys
import os
directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(directory)
sys.path.append(parent)
import cppm_helper

print(parent)

def test_extract_mac_oui_extracts_half_of_colon_separated_mac():
    mac = '00:1b:bc:16:00:c3'
    expected = '001bbc'
    generated = cppm_helper.extract_oui(mac)

    assert(generated == expected)

def test_get_vlan_from_port_information_extracts_vlan_id_from_information():
    port_info = 'vlan192'
    expected = '192'
    generated = cppm_helper.get_vlan_from_port_info(port_info)
    assert(generated == expected)


def test_get_vlan_from_port_info_returns_na_if_no_vlan_information():
    port_info = '1/1/24'
    expected = 'na'
    generated = cppm_helper.get_vlan_from_port_info(port_info)
    assert(generated == expected)

def test_extract_device_information_from_sh_mac_address_creates_a_dictionary_with_device_information():
    sh_line = [['64:e8:81:3f:06:40', '1', 'dynamic', '1/1/25']]
    expected = {
        '64:e8:81:3f:06:40': {
        'vlan' : '1',
        'type' : 'dynamic',
        'physical_port' : '1/1/25'
        }
    }
    mac = '64:e8:81:3f:06:40'
    generated = cppm_helper.extract_device_info_from_sh_mac_address(sh_line)
    assert(generated[mac]['vlan'] == expected[mac]['vlan'])
    assert(generated[mac]['type'] == expected[mac]['type'])
    assert(generated[mac]['physical_port'] == expected[mac]['physical_port'])

def test_add_ip_information_to_devices_adds_ip_information_if_it_exists():
    sh_line = [['10.10.90.20', '54:04:a6:0b:f8:51','vlan90','1/1/25']]
    mac = '54:04:a6:0b:f8:51'
    devices = {mac : { 'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25'} }
    expected = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20'}}
    
    cppm_helper.add_ip_information_to_devices(sh_line, devices)
    assert(devices[mac]['ip'] == expected[mac]['ip'])
    assert(devices[mac]['vlan'] == expected[mac]['vlan'])
    assert(devices[mac]['physical_port'] == expected[mac]['physical_port'])

def test_add_mac_oui_to_devices_adds_mac_oui_attribute_with_no_separators_to_devices():
    mac = '54:04:a6:0b:f8:51'
    devices = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20'}}
    expected = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20', 'mac_oui': '5404a6'}}
    cppm_helper.add_mac_oui_to_devices(devices)
    assert('5404a6' == expected[mac]['mac_oui'])

def test_add_mac_vendor_to_devices_adds_correct_mac_vendor_to_devices():
    mac = '54:04:a6:0b:f8:51'
    mac_vendor = 'ASUSTek COMPUTER INC.'
    devices = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20', 'mac_oui': '5404a6'}}
    expected = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20', 'mac_oui': '5404a6', 'mac_vendor': mac_vendor}}
    mac_vendors = {'5404A6':'ASUSTek COMPUTER INC.'}
    cppm_helper.add_mac_vendor_to_devices(devices, mac_vendors)
    assert('ASUSTek COMPUTER INC.' == expected[mac]['mac_vendor'])
    
def test_add_mac_vendor_to_devices_adds_na_to_devices_if_mac_oui_not_in_vendors_list():
    mac = '54:04:78:aa:bc:de'
    devices = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20', 'mac_oui': '5404a6'}}
    expected = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20', 'mac_oui': '5404a6', 'mac_vendor': 'na'}}
    mac_vendors = {'5404A6':'ASUSTek COMPUTER INC.'}
    cppm_helper.add_mac_vendor_to_devices(devices, mac_vendors)
    assert('na' == expected[mac]['mac_vendor'])

    