import sys
import os
directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(directory)
sys.path.append(parent)
import data_util
import excel_util
import file_util

def test_extract_mac_oui_extracts_half_of_colon_separated_mac():
    mac = '00:1b:bc:16:00:c3'
    expected = '001bbc'
    generated = data_util.extract_oui(mac)

    assert(generated == expected)

def test_get_vlan_from_port_information_extracts_vlan_id_from_information():
    port_info = 'vlan192'
    expected = '192'
    generated = data_util.get_vlan_from_port_info(port_info)
    assert(generated == expected)


def test_get_vlan_from_port_info_returns_na_if_no_vlan_information():
    port_info = '1/1/24'
    expected = 'na'
    generated = data_util.get_vlan_from_port_info(port_info)
    assert(generated == expected)

def test_extract_device_information_from_sh_mac_address_creates_a_dictionary_with_device_information():
    sh_line = [['64:e8:81:3f:06:40', '1', 'dynamic', '1/1/25']]
    sh_line_headers = ['MAC', 'VLAN', 'TYPE', 'PORT']
    expected = {
        '64:e8:81:3f:06:40': {
        'vlan' : '1',
        'physical_port' : '1/1/25'
        }
    }
    mac = '64:e8:81:3f:06:40'
    generated = data_util.extract_device_info_from_sh_mac_address(sh_line, sh_line_headers)
    assert(generated[mac]['vlan'] == expected[mac]['vlan'])
    assert(generated[mac]['physical_port'] == expected[mac]['physical_port'])

def test_add_ip_information_to_devices_adds_ip_information_if_it_exists():
    sh_line = [['10.10.90.20', '54:04:a6:0b:f8:51','vlan90','1/1/25']]
    sh_line_headers = ['IP','MAC','PORT','PHYSICAL_PORT']
    mac = '54:04:a6:0b:f8:51'
    devices = {mac : { 'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25'} }
    expected = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20'}}
    
    data_util.add_ip_information_to_devices(sh_line, sh_line_headers, devices)
    assert(devices[mac]['ip'] == expected[mac]['ip'])
    assert(devices[mac]['vlan'] == expected[mac]['vlan'])
    assert(devices[mac]['physical_port'] == expected[mac]['physical_port'])

def test_add_mac_oui_to_devices_adds_mac_oui_attribute_with_no_separators_to_devices():
    mac = '54:04:a6:0b:f8:51'
    devices = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20'}}
    expected = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20', 'mac_oui': '5404a6'}}
    data_util.add_mac_oui_to_devices(devices)
    assert('5404a6' == expected[mac]['mac_oui'])

def test_add_mac_vendor_to_devices_adds_correct_mac_vendor_to_devices():
    mac = '54:04:a6:0b:f8:51'
    mac_vendor = 'ASUSTek COMPUTER INC.'
    devices = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20', 'mac_oui': '5404a6'}}
    expected = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20', 'mac_oui': '5404a6', 'mac_vendor': mac_vendor}}
    mac_vendors = {'5404A6':'ASUSTek COMPUTER INC.'}
    data_util.add_mac_vendor_to_devices(devices, mac_vendors)
    assert('ASUSTek COMPUTER INC.' == expected[mac]['mac_vendor'])
    
def test_add_mac_vendor_to_devices_adds_na_to_devices_if_mac_oui_not_in_vendors_list():
    mac = '54:04:78:aa:bc:de'
    devices = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20', 'mac_oui': '5404a6'}}
    expected = {mac : {'vlan':'90', 'type': 'dynamic', 'physical_port':'1/1/25', 'ip' : '10.10.90.20', 'mac_oui': '5404a6', 'mac_vendor': 'na'}}
    mac_vendors = {'5404A6':'ASUSTek COMPUTER INC.'}
    data_util.add_mac_vendor_to_devices(devices, mac_vendors)
    assert('na' == expected[mac]['mac_vendor'])

def test_catalogue_devices_by_vendor_categorizes_device_numbers_correctly():
    devices = {'mac1': {'mac_vendor': 'SERRA SOLDADURA, S.A.'}, 
               'mac2': {'mac_vendor': 'CONTEMPORARY CONTROL'}, 
               'mac3': {'mac_vendor': 'CONTEMPORARY CONTROL'}, 
                'mac4': {'mac_vendor': 'TAS TELEFONBAU A. SCHWABE GMBH CO. KG'}, 
                'mac5': {'mac_vendor': 'CONTEMPORARY CONTROL'}, 
                'mac6': {'mac_vendor': 'TAS TELEFONBAU A. SCHWABE GMBH CO. KG'}, 
                'mac7': {'mac_vendor': 'CONTEMPORARY CONTROL'}, 
                'mac8': {'mac_vendor': '3COM'}, 
                'mac9': {'mac_vendor': 'CONTEMPORARY CONTROL'}, 
                'mac10': {'mac_vendor': 'CONTEMPORARY CONTROL'}, 
                'mac11': {'mac_vendor': '3COM'}, 
                'mac12': {'mac_vendor': 'TAS TELEFONBAU A. SCHWABE GMBH CO. KG'}, 
                'mac13': {'mac_vendor': '3COM'}, 
                'mac14': {'mac_vendor': 'TAS TELEFONBAU A. SCHWABE GMBH CO. KG'}, 
                'mac15': {'mac_vendor': '3COM'}, 
                'mac16': {'mac_vendor': '3COM'}, 
                'mac17': {'mac_vendor': 'CONTEMPORARY CONTROL'}, 
                'mac18': {'mac_vendor': 'TAS TELEFONBAU A. SCHWABE GMBH CO. KG'}, 
                'mac19': {'mac_vendor': '3COM'}, 
                'mac20': {'mac_vendor': '3COM'}}
    expected = {'SERRA SOLDADURA, S.A.': 1,
                'CONTEMPORARY CONTROL' : 7,
                'TAS TELEFONBAU A. SCHWABE GMBH CO. KG': 5,
                '3COM': 7}
    generated = data_util.catalogue_devices_by_vendor(devices)
    for vendor in expected:
        assert expected[vendor] == generated[vendor]

def test_get_widest_column_widths_returns_the_widest_column_widths_from_list_of_list():
    test_data = [
        ['001bbc', '001bbc-1600c3', '10.31.80.10', 'Silver Peak Systems, Inc.', '1/1/1', 80],
        ['b00cd1', 'b00cd1-5dea81', '10.4.255.255', 'Hewlett Packard', '1/1/3', 110],
        ['708bcd', '708bcd-b9fb0f', '', 'ASUSTek COMPUTER INC.', '1/1/22', 1230]
    ]
    expected = [8, 15, 14, 27, 8, 6]
    generated = excel_util.get_widest_column_widths(test_data)
    for e,g in zip(expected, generated):
        assert(e==g)

def test_combine_vendor_catalogue_data_adds_same_vendor_items_together():
    test_data = [
        {
            'data' : [['vendor1',20], ['vendor2',2],['vendor3',5]]
        },
        {
            'data' : [['vendor1',2],['vendor2',3],['vendor4',10]]
        }
    ]
    expected = {
        'name':'Number of devices by Vendor',
        'data' : [['vendor1',22], ['vendor2',5],['vendor3',5],['vendor4',10]],
        'style' : 'Table Sytle Medium 6'
        }
    generated = data_util.combine_vendor_catalogue_tables(test_data)
    expected_data = expected['data']
    generated_data = generated['data']
    for expected_pair, generated_pair in zip(expected_data,generated_data):
        assert(expected_pair[1] == generated_pair[1])

def test_remove_file_extension_from_name_removes_extension():
    filename = 'example.txt'
    expected = 'example'
    generated = file_util.remove_file_extension_from_filename(filename)
    assert(expected == generated)

def test_combine_vlan_tables_only_adds_unique_vlans_to_combined_table():
    test_data = [
        {'headers': ['VLAN', 'VLAN_NAME'], 'data':[['100', 'vlan100']]},
        {'headers': ['VLAN_NAME', 'VLAN'], 'data':[['vlan120', '120']]}
    ]
    expected = {
        'name': 'VLANs',
        'headers' : ['VLAN', 'VLAN_NAME'],
        'data' : [
            ['100', 'vlan100'],
            ['120', 'vlan120']
        ]
    }
    generated = data_util.combine_vlan_tables(test_data)
    expected_vlans = expected['data']
    generated_vlans = generated['data']
    for row_e,row_g in zip(expected_vlans, generated_vlans):
        assert(row_e[0] == row_g[0])
        assert(row_e[1] == row_g[1])
    assert(expected['name'] == generated['name'])
    assert(expected['headers'][0] == generated['headers'][0])
    assert(expected['headers'][1] == generated['headers'][1])

def test_create_vlan_table_from_show_mac_address_info_creates_a_vlan_table_with_default_names():
    test_data = {
        'devices' : 
            {
                'mac1': {
                    'vlan' : '20'
                },
                'mac2': {
                    'vlan' : '2089'
                },
                'mac3': {
                    'vlan' : '300'
                }
            }
        }
    
    expected = {
        'name' : 'VLANs',
        'style' : 'Table Style Medium 7',
        'data' : [
            ['20', 'VLAN20', '0x14',''],
            ['2089', 'VLAN2089', '0x829',''],
            ['300', 'VLAN300', '0x12c', '']
        ],
        'headers' : ['VLAN', 'VLAN_NAME', 'HEX', 'DECIMAL']
    }
    generated = data_util.create_host_vlan_table_from_sh_mac_address_info(test_data)
    assert expected['name'] == generated['name']
    assert expected['style'] == generated['style']
    assert expected['headers'] == generated['headers']
    for row_e, row_g in zip(expected['data'], generated['data']):
        for ele_e, ele_g in zip(row_e, row_g):
            assert(ele_e == ele_g)

def test_create_vlan_table_from_show_mac_address_info_creates_a_vlan_table_without_duplicate_vlans():
    test_data = {
        'devices' : 
            {
                'mac1': {
                    'vlan' : '20'
                },
                'mac2': {
                    'vlan' : '2089'
                },
                'mac3': {
                    'vlan' : '300'
                },
                'mac4': {
                    'vlan' : '20'
                },
                'mac5': {
                    'vlan' : '2089'
                }
            }
        }
    
    expected = {
        'name' : 'VLANs',
        'style' : 'Table Style Medium 7',
        'data' : [
            ['20', 'VLAN20', '0x14',''],
            ['2089', 'VLAN2089', '0x829',''],
            ['300', 'VLAN300', '0x12c', '']
        ],
        'headers' : ['VLAN', 'VLAN_NAME', 'HEX', 'DECIMAL']
    }
    generated = data_util.create_host_vlan_table_from_sh_mac_address_info(test_data)
    assert expected['name'] == generated['name']
    assert expected['style'] == generated['style']
    assert expected['headers'] == generated['headers']
    for row_e, row_g in zip(expected['data'], generated['data']):
        for ele_e, ele_g in zip(row_e, row_g):
            assert(ele_e == ele_g)