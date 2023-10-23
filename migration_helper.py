import file_util
import excel_util
import data_util
import os


templates = ['sh_int_status.template',
             'sh_run_int.template',
             'sh_lldp_in_re_de.template', 
             'sh_cdp_ne_de.template', 
             'sh_run_vlans.template',
             'run_radius.template', 
             'ip_dns_server_address.template', 
             'ip_dns_domain_name.template', 
             'snmp_community.template',
             'sh_system.template',
             'sh_module.template',
             'ntp_server_ip.template']

BASE_TABLE_INDICES = {
    'sh_run_vlans' : templates.index('sh_run_vlans.template'),
    'sh_system' : templates.index('sh_system.template'),
    'sh_module' : templates.index('sh_module.template'),
    'sh_lldp_in_re_de' : templates.index('sh_lldp_in_re_de.template'),
    'sh_cdp_ne_de' : templates.index('sh_cdp_ne_de.template'),
    'sh_int_status' : templates.index('sh_int_status.template'),
    'sh_run_int' : templates.index('sh_run_int.template'),
    'ip_dns_server_address' : templates.index('ip_dns_server_address.template'),
    'ip_dns_domain_name' : templates.index('ip_dns_domain_name.template'),
    'ntp_server_ip' : templates.index('ntp_server_ip.template'),
}

supported_oses = ['aos-s']
cwd = os.getcwd()
device_names = []
device_names_populated = False
templates_folder = os.path.join(cwd, 'templates')
host_index = 1
for supported_os in supported_oses:
    aos_s_templates_folder = os.path.join(templates_folder, supported_os)
    results = []
    worksheet_names = []
    tables = []
    show_file_path = os.path.join(cwd,'show_files')
    show_files_os_path = os.path.join(show_file_path, supported_os)
    show_files = os.listdir(show_files_os_path)
    for show_file in show_files:
        show_filepath = os.path.join(show_files_os_path, show_file)
        print(f'Parsing information in file {show_file}...')
        current_device = []
        for template in templates:
            template_filepath = os.path.join(aos_s_templates_folder, template)
            current_device.append(file_util.extract_table_from_config_file(template_filepath, show_filepath))
        new_table = data_util.remove_trunk_from_port_name(current_device[0])
        current_device[0] = new_table
        results.append(current_device)
        if not device_names_populated:
            with open(show_filepath) as sf:
                sf_lines = sf.readlines()
                hostname = data_util.extract_hostname_from_cli_output(sf_lines)
                device_names.append(hostname)

    worksheet_names.append('Overview')

    all_systems = {}
    systems_data = []
    systems_table = {}

    dns_table = {}
    dns_all_systems = {}
    dns_systems_table = {}
    overview_tables = []
    overview_first_column = []

    ip_helper_table = {}
    ip_helper_all_systems = {}
    ip_helper_systems_table = {}

    ntp_ip_table = {}
    ntp_ip_all_systems = {}
    ntp_ip_systems_table = {}

    for device_name, device in zip(device_names, results):
        print(f'gathering DNS information for {device_name}...')
        dns_headers_to_include = ['DNS_IP']
        dns_table = data_util.create_base_table(device[BASE_TABLE_INDICES['ip_dns_server_address']], dns_headers_to_include,'DNS_IP', dns_all_systems)

        print(f'gathering IP helper address information for {device_name}...')
        ip_helper_headers_to_include = ['VLAN_ID', 'IP_HELPER_ADDRESS']
        ip_helper_table = data_util.create_base_table(device[BASE_TABLE_INDICES['sh_run_vlans']], ip_helper_headers_to_include, 'VLAN_ID',ip_helper_all_systems)

        print(f'gathering NTP information for {device_name}...')
        ntp_ip_headers_to_include = ['NTP_SERVER_IP']
        ntp_ip_table = data_util.create_base_table(device[BASE_TABLE_INDICES['ntp_server_ip']], ntp_ip_headers_to_include, 'NTP_SERVER_IP', ntp_ip_all_systems)

    dns_systems_table['headers'] = ['DNS_IP']
    dns_systems_table['name'] = 'DNS'
    dns_systems_table['data'] = dns_all_systems
    dns_systems_table_data = data_util.convert_dictionary_to_table_structure(dns_systems_table)
    dns_systems_table['data'] = dns_systems_table_data
    
    overview_first_column.append(dns_systems_table)

    helper_ip_set = set()
    helper_ips = []
    for vlan_id, helpers in ip_helper_all_systems.items():
        if len(helpers['IP_HELPER_ADDRESS']) > 0:
            for helper_ip in helpers['IP_HELPER_ADDRESS']:
                if not helper_ip in helper_ip_set:
                    helper_ip_set.add(helper_ip)
                    helper_ips.append([helper_ip])
    ip_helper_systems_table['name'] = 'DHCP'
    ip_helper_systems_table['data'] = helper_ips
    ip_helper_systems_table['headers'] = ['IP_HELPER_ADDRESS']
    overview_first_column.append(ip_helper_systems_table)

    ntp_ip_systems_table['name'] = 'NTP'
    ntp_ip_systems_table['headers'] = ['NTP_SERVER_IP']
    ntp_ip_systems_table['data'] = ntp_ip_all_systems
    ntp_ip_systems_table_data = data_util.convert_dictionary_to_table_structure(ntp_ip_systems_table)
    ntp_ip_systems_table['data'] = ntp_ip_systems_table_data
    overview_first_column.append(ntp_ip_systems_table)

    overview_tables.append(overview_first_column)

    for device_name, device in zip(device_names, results):

        print(f'gathering system information for {device_name}...')
        headers_to_include = ['SYSTEM_NAME', 'SOFTWARE_VERSION', 'SERIAL_NUMBER']        
        system_table = data_util.create_base_table(device[BASE_TABLE_INDICES['sh_system']],headers_to_include,'SERIAL_NUMBER',all_systems)

        system_outputs = {}
        system_outputs['sh_module'] = {
            'parsed_data' : device[BASE_TABLE_INDICES['sh_module']],
            'new_headers' : {
                'CHASSIS_MODEL' : {
                    'index' : 0,
                    'new_name' : 'CHASSIS_MODEL'
                },
            }
        }
        matched_parameter_index = 1
        data_util.add_new_info_from_other_tables_to_table(system_table, system_outputs, matched_parameter_index)
        
    systems_table['headers'] = [
        'SERIAL_NUMBER',
        'SYSTEM_NAME',
        'CHASSIS_MODEL',
        'SOFTWARE_VERSION'
    ]
    systems_table['name'] = 'System Info'
    systems_table['data'] = all_systems
    systems_table_data = data_util.convert_dictionary_to_table_structure(systems_table)
    systems_table['data'] = systems_table_data

    new_header_order = [
        'LOCATION',
        'SUB_LOCATION',
        'SYSTEM_NAME',
        'MGMT_IP',
        'MGMT_SOURCE',
        'CHASSIS_MODEL',
        'SERIAL_NUMBER',
        'SOFTWARE_VERSION'
    ]

    reordered_table = data_util.reorder_table_based_on_new_header_order([systems_table['headers'],systems_table['data']], new_header_order)
    systems_table['data'] = reordered_table[1]
    systems_table['headers'] = reordered_table[0] 
    systems_table['name'] = 'system_info'
    overview_second_column = []
    overview_second_column.append(systems_table)
    overview_tables.append(overview_second_column)
    tables.append(overview_tables)

    all_vlans = set()
    for device in results:
        device_vlans = device[BASE_TABLE_INDICES['sh_run_vlans']]
        device_vlan_headers = device_vlans[0]
        device_vlan_data = device_vlans[1]
        vlan_id_index = device_vlan_headers.index('VLAN_ID')
        for vlan in device_vlan_data:
            vlan_id = vlan[vlan_id_index]
            if not vlan_id in all_vlans:
                all_vlans.add(vlan_id)

    for device in results:
        device_vlans = device[BASE_TABLE_INDICES['sh_run_vlans']]
        device_vlan_headers = device_vlans[0]
        device_vlan_data = device_vlans[1]
        vlan_id_index = device_vlan_headers.index('VLAN_ID')
        vlans_not_in_device_vlans = []
        device_vlans = set()
        for vlan in device_vlan_data:
            vlan_id = vlan[vlan_id_index]
            device_vlans.add(vlan_id)
        for vlan in all_vlans:
            if not vlan in device_vlans:
                vlan_row = [vlan]
                for header in device_vlan_headers[1:]:
                    vlan_row.append('')
                device_vlan_data.append(vlan_row)
        device_vlan_data.sort(key=lambda x : int(x[0]))

    vlan_tables = []
    worksheet_names.append('Layer 2 & 3')
    tables.append(vlan_tables)

    for device_name, device in zip(device_names, results):

        print(f'aggregating L2/3 information into tables...')
        headers_to_include = ['VLAN_ID', 'VLAN_NAME']
        sh_run_vlans = device[4]
        vlan_table = data_util.create_base_table(sh_run_vlans,headers_to_include,'VLAN_ID')
        converted_ip_addresses = data_util.convert_vlan_ip_subnet_to_slash_notation(sh_run_vlans)
        
        vlan_outputs = {}
        vlan_outputs['ip_address_converted'] = {
            'parsed_data' : converted_ip_addresses,
            'new_headers' : {
                'IP_ADDRESS' : {
                    'index' : 0,
                    'new_name' : 'IP_ADDRESS'
                }
            }
        }

        data_util.add_new_info_from_other_tables_to_table(vlan_table,vlan_outputs)
        data_table = data_util.convert_dictionary_to_table_structure(vlan_table)
        vlan_table['data'] = data_table
        vlan_table['name'] = device_name 

        vlan_tables.append([vlan_table])

        headers = device[1][0]
        device_data = device[1]
        port_table = data_util.create_base_table(device_data,headers,'INTERFACE',{})

        outputs = {
            'sh_cdp_ne_de' : {
            'parsed_data' : device[BASE_TABLE_INDICES['sh_cdp_ne_de']],
            'new_headers' : {
                'IP_ADDRESS' : {
                    'index' : 0,
                    'new_name' : 'NEIGHBOR_IP'
                },
                'PLATFORM' : {
                    'index' : 0,
                    'new_name' : 'NEIGHBOR_PLATFORM'
                }
            }
            },
        'lldp_neighbors' : {
            'parsed_data' : device[BASE_TABLE_INDICES['sh_lldp_in_re_de']],
            'new_headers' : {
                'SYSTEM_NAME' : {
                    'index' : 0,
                    'new_name' : 'NEIGHBOR_NAME'
                }
            }   
        },
        'sh_int_status' : {
            'parsed_data' : device[BASE_TABLE_INDICES['sh_int_status']],
            'new_headers' : {
                h : {
                    'index' : 0,
                    'new_name' : h
                } for h in device[BASE_TABLE_INDICES['sh_int_status']][0][2:len(device[BASE_TABLE_INDICES['sh_int_status']][0])-2]
            }
        }
        }

        data_util.add_new_info_from_other_tables_to_table(port_table, outputs)
        
        new_header_order = [
        'INTERFACE',
        'NAME',
        'NEIGHBOR_IP',
        'NEIGHBOR_NAME',
        'NEIGHBOR_PLATFORM',
        'STATUS',
        'CONFIG_MODE',
        'SPEED',
        'TYPE',
        'TRUNK',
        'TAGGED_VLAN',
        'UNTAGGED_VLAN'
        ]
        port_table['headers'] = new_header_order
        data_table = data_util.convert_dictionary_to_table_structure(port_table)
        port_table['data'] = data_table
        if device_name == '':
            port_table['name'] = f'host{host_index}'
            host_index += 1
        else:
            port_table['name'] = device_name
        worksheet_names.append(port_table['name'])
        print(f'writing port/interface table to excel file for {device_name}...')
        tables.append([[port_table]])

    print('saving excel file to migration.xlsx')
    excel_util.write_tables_to_excel_worksheets('migration.xlsx',worksheet_names,tables)