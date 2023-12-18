import sys
import os
directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(directory)
sys.path.append(parent)
import data_util
import excel_util
import file_util
import data_structures
import pytest

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
        {'headers': ['VLAN', 'VLAN_NAME', 'HEX', 'DECIMAL'], 'data':[['100', 'vlan100', '0x64', '']]},
        {'headers': ['VLAN', 'VLAN_NAME', 'HEX', 'DECIMAL'], 'data':[['120', 'vlan120', '0x78', '']]}
    ]
    expected = {
        'name': 'VLANs',
        'headers' : ['VLAN', 'VLAN_NAME', 'HEX', 'DECIMAL'],
        'data' : [
            ['100', 'vlan100', '0x64', ''],
            ['120', 'vlan120', '0x78', '']
        ]
    }
    generated = data_util.combine_vlan_tables(test_data)
    expected_vlans = expected['data']
    generated_vlans = generated['data']
    for row_e,row_g in zip(expected_vlans, generated_vlans):
        assert(row_e[0] == row_g[0])
        assert(row_e[1] == row_g[1])
    assert(expected['name'] == generated['name'])
    e_headers = expected['headers']
    g_headers = generated['headers']
    for e_header,g_header in zip(e_headers, g_headers):
        assert(e_header == g_header)
    e_data = expected['data']
    g_data = generated['data']
    for e_data,g_data in zip(e_data, g_data):
        assert(e_data == g_data)

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

def test_convert_subnet_mask_to_subnet_length_raises_error_for_invalid_octect_values():
    with pytest.raises(ValueError) as ve:
        generated = data_util.convert_subnet_mask_to_subnet_length('255.255.255.111')

def test_convert_subnet_mask_to_subnet_length_converts_all_lengths_correctly():
    cases = [
        '0.0.0.0',
        '128.0.0.0',
        '192.0.0.0',
        '224.0.0.0',
        '240.0.0.0',
        '248.0.0.0',
        '252.0.0.0',
        '254.0.0.0',
        '255.0.0.0',
        '255.128.0.0',
        '255.192.0.0',
        '255.224.0.0',
        '255.240.0.0',
        '255.248.0.0',
        '255.252.0.0',
        '255.254.0.0',
        '255.255.0.0',
        '255.255.128.0',
        '255.255.192.0',
        '255.255.224.0',
        '255.255.240.0',
        '255.255.248.0',
        '255.255.252.0',
        '255.255.254.0',
        '255.255.255.0',
        '255.255.255.128',
        '255.255.255.192',
        '255.255.255.224',
        '255.255.255.240',
        '255.255.255.248',
        '255.255.255.252',
        '255.255.255.254',
        '255.255.255.255',
    ]
    for index,case in enumerate(cases):
        case_len = data_util.convert_subnet_mask_to_subnet_length(case)
        assert int(case_len) == index

def test_process_trunks_returns_original_table_when_no_trunks_exist():
    test_data = [
        ['INTERFACE_NAME', 'TAGGED_VLAN', 'UNTAGGED_VLAN', 'TRUNK'],
        [['A1', '', '1', ''],
        ['A2', '1,20,45,100', '10', ''],
        ['A3', '', '1', '']]
    ]
    generated = data_util.process_trunks('aos-s', test_data)
    for e_row, g_row in zip(test_data, generated):
        for e_item, g_item in zip(e_row, g_row):
            assert e_item == g_item

def test_process_trunks_groups_interfaces_under_trunks():
    test_data = [
        ['INTERFACE_NAME', 'TAGGED_VLAN', 'UNTAGGED_VLAN', 'TRUNK'],
        [['A1', '10,20,30', '40', 'trk15 lacp'],
        ['A2', '10,20,30', '40', 'trk16 lacp'],
        ['A3', '10,20,30', '40', 'trk17 lacp'],
        ['B1', '10,20,30', '40', 'trk15 lacp'],
        ['B2', '10,20,30', '40', 'trk16 lacp'],
        ['B3', '10,20,30', '40', 'trk17 lacp'],
        ['Trk15', '10,20,30', '40', ''],
        ['Trk16', '10,20,30', '40', ''],
        ['Trk17', '10,20,30', '40', ''],]
    ]
    expected = [
        ['INTERFACE_NAME', 'TAGGED_VLAN', 'UNTAGGED_VLAN', 'TRUNK'],
        [['Trk15', '10,20,30', '40', ''],
        ['A1', '10,20,30', '40', 'trk15 lacp'],
        ['B1', '10,20,30', '40', 'trk15 lacp'],
        ['Trk16', '10,20,30', '40', ''],
        ['A2', '10,20,30', '40', 'trk16 lacp'],
        ['B2', '10,20,30', '40', 'trk16 lacp'],
        ['Trk17', '10,20,30', '40', ''],
        ['A3', '10,20,30', '40', 'trk17 lacp'],
        ['B3', '10,20,30', '40', 'trk17 lacp'],]
    ]
    generated = data_util.process_trunks('aos-s', test_data)
    for e_row, g_row in zip(expected, generated):
        for e_item, g_item in zip(e_row, g_row):
            assert e_item == g_item

def test_process_trunks_includes_non_trunk_interfaces_with_trunk_interfaces():
    test_data = [
        ['INTERFACE_NAME', 'TAGGED_VLAN', 'UNTAGGED_VLAN', 'TRUNK'],
        [['A1', '10,20,30', '40', 'trk15 lacp'],
        ['A2', '10,20,30', '40', 'trk16 lacp'],
        ['A3', '10,20,30', '40', 'trk17 lacp'],
        ['B1', '10,20,30', '40', 'trk15 lacp'],
        ['B2', '10,20,30', '40', 'trk16 lacp'],
        ['B3', '10,20,30', '40', 'trk17 lacp'],
        ['B4', '10,20,30', '40', ''],
        ['B5', '10,20,30', '40', ''],
        ['Trk15', '10,20,30', '40', ''],
        ['Trk16', '10,20,30', '40', ''],
        ['Trk17', '10,20,30', '40', ''],]
    ]
    expected = [
        ['INTERFACE_NAME', 'TAGGED_VLAN', 'UNTAGGED_VLAN', 'TRUNK'],
        [['B4', '10,20,30', '40', ''],
        ['B5', '10,20,30', '40', ''],
        ['Trk15', '10,20,30', '40', ''],
        ['A1', '10,20,30', '40', 'trk15 lacp'],
        ['B1', '10,20,30', '40', 'trk15 lacp'],
        ['Trk16', '10,20,30', '40', ''],
        ['A2', '10,20,30', '40', 'trk16 lacp'],
        ['B2', '10,20,30', '40', 'trk16 lacp'],
        ['Trk17', '10,20,30', '40', ''],
        ['A3', '10,20,30', '40', 'trk17 lacp'],
        ['B3', '10,20,30', '40', 'trk17 lacp'],]
    ]
    generated = data_util.process_trunks('aos-s', test_data)
    for e_row, g_row in zip(expected, generated):
        for e_item, g_item in zip(e_row, g_row):
            assert e_item == g_item

def test_remove_trunk_from_port_name_removes_the_trailing_trunk_portion_from_all_trunk_members():
    test_data = [
        ['PORT', 'NAME', 'STATUS', 'CONFIG_MODE', 'SPEED', 'TYPE', 'TAGGED', 'UNTAGGED'],
        [
            ['A1-Trk15', 'D122i', 'Down', '', '', '', 'multi', '1'],
            ['A2-Trk20', 'D105B-S...', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'multi', '1'],
            ['A3-Trk25', 'D105B-A...', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'multi', '1'],
            ['A4-Trk30', 'D105B-HP', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'multi', '1'],
            ['A5', 'D200', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'multi', '1'],
            ['A6', 'Aruba92...', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'multi', '15'],
            ['A7', 'open - ...', 'Down', '', '', '', 'multi', '15'],
            ['A8', 'COMCAST', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'No', '213'],
        ]
    ]
    
    expected = [
        ['PORT', 'NAME', 'STATUS', 'CONFIG_MODE', 'SPEED', 'TYPE', 'TAGGED', 'UNTAGGED'],
        [
            ['A1', 'D122i', 'Down', '', '', '', 'multi', '1'],
            ['A2', 'D105B-S...', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'multi', '1'],
            ['A3', 'D105B-A...', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'multi', '1'],
            ['A4', 'D105B-HP', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'multi', '1'],
            ['A5', 'D200', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'multi', '1'],
            ['A6', 'Aruba92...', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'multi', '15'],
            ['A7', 'open - ...', 'Down', '', '', '', 'multi', '15'],
            ['A8', 'COMCAST', 'Up', 'Auto', '10GigFD', '10GbE-GEN', 'No', '213'],
        ]
    ]
    generated = data_util.remove_trunk_from_port_name(test_data)
    expected_ports = expected[1]
    generated_ports = generated[1]
    for e_port, g_port in zip(expected_ports, generated_ports):
        for e_item, g_item in zip(e_port, g_port):
            assert e_item == g_item

def test_extract_hostname_from_cli_output_extracts_hostname_on_show_command_lines():
    test_data = [
        'host1#\n',
        '\n',
        'host1# sh run int\n',
    ]
    expected = 'host1'
    generated = data_util.extract_hostname_from_cli_output(test_data)
    assert expected == generated

def test_extract_hostname_from_cli_output_returns_empty_string_when_no_host_prompt_exists():
    test_data = [
        'some table\n',
        'data1 data2 data3\n',
        'end table\n'
    ]
    expected = ''
    generated = data_util.extract_hostname_from_cli_output(test_data)
    assert expected == generated

def test_convert_vlan_ip_subnet_to_slash_notation_converts_ip_address_subnet_mask_correctly():
    test_data = [
        ['VLAN_ID', 'VLAN_NAME', 'IP_ADDRESS', 'SUBNET', 'IP_HELPER_ADDRESS'],
        [
            ['1', 'DEFAULT_VLAN', '', '', []],
            ['2', 'StaffVLAN', '10.200.1.1', '255.255.255.0', []],
            ['3', 'VLAN3', '10.3.3.3', '255.255.0.0', []]
        ]
    ]
    expected = [
        ['VLAN_ID', 'IP_ADDRESS'],
        [
            ['1', ''],
            ['2', '10.200.1.1/24'],
            ['3', '10.3.3.3/16']
        ]
    ]
    generated = data_util.convert_vlan_ip_subnet_to_slash_notation(test_data)
    e_headers = expected[0]
    g_headers = generated[0]
    for e_header, g_header in zip(e_headers,g_headers):
        assert e_header == g_header
    
    e_vlan_data = expected[1]
    g_vlan_data = generated[1]
    for e_row, g_row in zip(e_vlan_data, g_vlan_data):
        for e_item, g_item in zip(e_row, g_row):
            assert e_item == g_item 


def test_reorder_table_based_on_new_header_order_reorders_correctly_without_extra_columns_added():
    test_data = [
        ['VLAN_ID', 'VLAN_NAME', 'IP_ADDRESS', 'SUBNET', 'IP_HELPER_ADDRESS'],
        [
            ['1', 'DEFAULT_VLAN', '', '', []],
            ['2', 'StaffVLAN', '10.200.1.1', '255.255.255.0', []],
            ['3', 'VLAN3', '10.3.3.3', '255.255.0.0', ['10.10.10.10']]
        ]
    ]
    new_headers_order = [
        'VLAN_NAME',
        'IP_HELPER_ADDRESS',
        'VLAN_ID',
        'IP_ADDRESS',
        'SUBNET'
    ]
    expected = [
        ['VLAN_NAME', 'IP_HELPER_ADDRESS', 'VLAN_ID', 'IP_ADDRESS', 'SUBNET'],
        [
            ['DEFAULT_VLAN', [], '1', '', ''],
            ['StaffVLAN', [], '2', '10.200.1.1', '255.255.255.0'],
            ['VLAN3', ['10.10.10.10'], '3', '10.3.3.3', '255.255.0.0']
        ]
    ]

    generated = data_util.reorder_table_based_on_new_header_order(test_data, new_headers_order)
    e_headers = expected[0]
    e_data = expected[1]
    g_headers = generated[0]
    g_data = generated[1]
    for e_header, g_header in zip(e_headers,g_headers):
        assert e_header == g_header
    for e_row,g_row in zip(e_data,g_data):
        for e_item,g_item in zip(e_row,g_row):
            assert e_item == g_item

def test_reorder_table_based_on_new_header_order_reorders_correctly_and_adds_extra_columns():
    test_data = [
        ['VLAN_ID', 'VLAN_NAME', 'IP_ADDRESS', 'SUBNET', 'IP_HELPER_ADDRESS'],
        [
            ['1', 'DEFAULT_VLAN', '', '', []],
            ['2', 'StaffVLAN', '10.200.1.1', '255.255.255.0', []],
            ['3', 'VLAN3', '10.3.3.3', '255.255.0.0', ['10.10.10.10']]
        ]
    ]
    new_headers_order = [
        'VLAN_NAME',
        'IP_HELPER_ADDRESS',
        'EXTRA1',
        'VLAN_ID',
        'IP_ADDRESS',
        'SUBNET',
    ]
    expected = [
        ['VLAN_NAME', 'IP_HELPER_ADDRESS', 'EXTRA1', 'VLAN_ID', 'IP_ADDRESS', 'SUBNET',],
        [
            ['DEFAULT_VLAN', [], '', '1', '', ''],
            ['StaffVLAN', [], '', '2', '10.200.1.1', '255.255.255.0'],
            ['VLAN3', ['10.10.10.10'], '', '3', '10.3.3.3', '255.255.0.0']
        ]
    ]

    generated = data_util.reorder_table_based_on_new_header_order(test_data, new_headers_order)
    e_headers = expected[0]
    e_data = expected[1]
    g_headers = generated[0]
    g_data = generated[1]
    for e_header, g_header in zip(e_headers,g_headers):
        assert e_header == g_header
    for e_row,g_row in zip(e_data,g_data):
        for e_item,g_item in zip(e_row,g_row):
            assert e_item == g_item

def test_create_outputs_ds_creates_expected_ds():
    test_data = [
        ['VLAN_ID', 'VLAN_NAME', 'IP_ADDRESS', 'SUBNET', 'IP_HELPER_ADDRESS'],
        [
            ['1', 'DEFAULT_VLAN', '', '', []],
            ['2', 'StaffVLAN', '10.200.1.1', '255.255.255.0', []],
            ['3', 'VLAN3', '10.3.3.3', '255.255.0.0', ['10.10.10.10']]
        ]
    ]
    device_info = [test_data]
    table_info = {
        'table_name' : 'test',
        'table_index' : 0,
        'headers_to_add' : [('VLAN_ID', 'VLAN'), ('IP_ADDRESS', 'IP')]
    }
    generated = data_util.create_outputs_ds(device_info, [table_info])
    assert 'test' in generated.keys()
    assert generated['test']['parsed_data'] == test_data
    assert generated['test']['new_headers']['VLAN_ID']['index'] == 0
    assert generated['test']['new_headers']['VLAN_ID']['new_name'] == 'VLAN'
    assert generated['test']['new_headers']['IP_ADDRESS']['index'] == 0
    assert generated['test']['new_headers']['IP_ADDRESS']['new_name'] == 'IP'

def test_merge_tables_into_one_returns_a_merged_table_from_two_tables():
    table1 = (
        ['header1', 'header2', 'header3'],
        [
            ['item1', 'item2', 'item3']
        ]
    )
    table2 = (
        ['header1', 'header2'],
        [
            ['item4', 'item5']
        ]
    )
    tables = [table1, table2]
    expected = (
        ['header1', 'header2', 'header3'],
        [
            ['item1', 'item2', 'item3'],
            ['item4', 'item5', '']
        ]
    )
    generated = data_util.merge_tables_into_one_table(tables)
    assert expected[0] == generated[0]
    assert expected[1] == expected[1]

def test_process_mgmt_int_information_adds_int_vlan_info_when_vlan_id_is_given():
    current_device_info = [
        {
            'headers' : [
                'MGMT_IP',
                'MGMT_SOURCE'
            ],
        }
    ]
    new_row = ['','']
    device = [('', '') for _ in data_structures.os_templates['aos-cx']]
    device[data_structures.os_templates['aos-cx'].index('sh_run_int_vlans.template')] = (['VLAN_ID', 'IP_ADDRESS'], [['33', '10.1.1.33/24']])
    data_util.process_mgmt_int_information('vlan 33', 'aos-cx', current_device_info,device,new_row)
    assert new_row[0] == '10.1.1.33/24'
    assert new_row[1] == 'VLAN 33'