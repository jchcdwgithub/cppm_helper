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
             'snmp_server_host.template',
             'snmp_community.template',
             'sh_system.template',
             'sh_module.template',
             'ntp_server_ip.template',
             'run_radius.template']

BASE_TABLE_INDICES = {
    'sh_run_vlans' : templates.index('sh_run_vlans.template'),
    'sh_system' : templates.index('sh_system.template'),
    'sh_module' : templates.index('sh_module.template'),
    'sh_lldp_in_re_de' : templates.index('sh_lldp_in_re_de.template'),
    'sh_cdp_ne_de' : templates.index('sh_cdp_ne_de.template'),
    'sh_int_status' : templates.index('sh_int_status.template'),
    'sh_run_int' : templates.index('sh_run_int.template'),
    'snmp_server_host' : templates.index('snmp_server_host.template'),
    'ip_dns_server_address' : templates.index('ip_dns_server_address.template'),
    'ip_dns_domain_name' : templates.index('ip_dns_domain_name.template'),
    'ntp_server_ip' : templates.index('ntp_server_ip.template'),
    'run_radius' : templates.index('run_radius.template'),
}

workbook = {
    'L2/L3' : [
        [
            {
                'table_name' : '',
                'base_table' : {
                    'base_table_index' : BASE_TABLE_INDICES['sh_run_vlans'],
                    'headers_to_include' : ['VLAN_ID', 'VLAN_NAME', 'IP_ADDRESS'],
                    'key' : 'VLAN_ID'
                },
                'final_headers' : ['VLAN_ID', 'VLAN_NAME', 'IP_ADDRESS'],
                'convert_table' : True
            }
        ]
    ],
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

    radius_table = {}
    radius_all_systems = {}
    radius_systems_table = {}

    snmp_table = {}
    snmp_all_systems = {}
    snmp_systems_table = {}

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

        print(f'gathering RADIUS information for {device_name}...')
        radius_headers_to_include = ['RADIUS_HOST']
        radius_table = data_util.create_base_table(device[BASE_TABLE_INDICES['run_radius']], radius_headers_to_include, 'RADIUS_HOST', radius_all_systems)

        print(f'gathering SNMP information for {device_name}...')
        snmp_headers_to_include = ['SNMP_SERVER_IP']
        snmp_table = data_util.create_base_table(device[BASE_TABLE_INDICES['snmp_server_host']], snmp_headers_to_include, 'SNMP_SERVER_IP', snmp_all_systems)

    dns_systems_table = data_util.create_excel_printable_table('DNS', dns_all_systems, ['DNS_IP'])
    overview_first_column.append(dns_systems_table)

    helper_ip_set = set()
    helper_ips = []
    for vlan_id, helpers in ip_helper_all_systems.items():
        if len(helpers['IP_HELPER_ADDRESS']) > 0:
            for helper_ip in helpers['IP_HELPER_ADDRESS']:
                if not helper_ip in helper_ip_set:
                    helper_ip_set.add(helper_ip)
                    helper_ips.append([helper_ip])

    ip_helper_systems_table = data_util.create_excel_printable_table('DHCP', helper_ips, ['IP_HELPER_ADDRESS'], convert_table=False)
    overview_first_column.append(ip_helper_systems_table)

    ntp_ip_systems_table = data_util.create_excel_printable_table('NTP', ntp_ip_all_systems, ['NTP_SERVER_IP'])
    overview_first_column.append(ntp_ip_systems_table)

    radius_systems_table = data_util.create_excel_printable_table('RADIUS', radius_all_systems, ['RADIUS_HOST'])
    overview_first_column.append(radius_systems_table)

    snmp_systems_table = data_util.create_excel_printable_table('SNMP', snmp_all_systems, ['SNMP_SERVER_IP'])
    overview_first_column.append(snmp_systems_table)

    overview_tables.append(overview_first_column)

    all_rows = []
    all_systems = {}

    for device_name, device in zip(device_names, results):
        system_table = [{
                'table_name' : 'system_info',
                'base_table' : {
                    'base_table_index' : BASE_TABLE_INDICES['sh_system'],
                    'headers_to_include' : ['SYSTEM_NAME', 'SOFTWARE_VERSION', 'SERIAL_NUMBER'],
                    'key' : 'SERIAL_NUMBER'
                },
                'parsed_info_to_add' : [
                    {
                        'table_name' : 'sh_module',
                        'table_index' : BASE_TABLE_INDICES['sh_module'],
                        'headers_to_add' : [
                            ('CHASSIS_MODEL', 'CHASSIS_MODEL')
                        ],
                    }
                ],
                'final_headers' : ['LOCATION', 'SUB_LOCATION', 'SYSTEM_NAME', 'MGMT_IP', 'MGMT_SOURCE', 'CHASSIS_MODEL', 'SERIAL_NUMBER', 'SOFTWARE_VERSION'],
                'convert_table' : True,
                'matched_parameter_index' : 1
            }]
        if all_systems == {}:
            all_systems = data_util.create_column_ds(system_table, device)
        else:
            current_device_info = data_util.create_column_ds(system_table, device)
            new_row = current_device_info[0]['data'][0]
            all_systems[0]['data'].append(new_row)

    overview_tables.append(all_systems)
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
        current_table = data_util.create_column_ds(workbook['L2/L3'][0], device)
        current_table[0]['name'] = device_name
        vlan_tables.append(current_table)

        #sh_run_vlans = device[4]
        #converted_ip_addresses = data_util.convert_vlan_ip_subnet_to_slash_notation(sh_run_vlans)

        device_port_table = [
            {
                'table_name' : device_name,
                'base_table' : {
                    'base_table_index' : BASE_TABLE_INDICES['sh_run_int'],
                    'headers_to_include' : ['INTERFACE', 'NAME', 'UNTAGGED_VLAN', 'TAGGED_VLAN'],
                    'key': 'INTERFACE'
                },
                'parsed_info_to_add': [
                    {
                        'table_name' : 'sh_cdp_ne_de',
                        'table_index' : BASE_TABLE_INDICES['sh_cdp_ne_de'],
                        'headers_to_add' : [
                            ('IP_ADDRESS', 'NEIGHBOR_IP'),
                            ('PLATFORM', 'NEIGHBOR_PLATFORM')
                        ]
                    },
                    {
                        'table_name' : 'lldp_neighbors',
                        'table_index' : BASE_TABLE_INDICES['sh_lldp_in_re_de'],
                        'headers_to_add' : [
                            ('SYSTEM_NAME', 'NEIGHBOR_NAME')
                        ]
                    },
                    {
                        'table_name' : 'sh_int_status',
                        'table_index' : BASE_TABLE_INDICES['sh_int_status'],
                        'headers_to_add' : [
                            (h, h) for h in device[BASE_TABLE_INDICES['sh_int_status']][0][2:len(device[BASE_TABLE_INDICES['sh_int_status']][0])-2]
                        ]
                    }
                ],
                'final_headers' : [
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
                            ],
                'convert_table' : True
            }
        ]
        port_table = data_util.create_column_ds(device_port_table, device)
        #if device_name == '':
        #    port_table['name'] = f'host{host_index}'
        #    host_index += 1
        #else:
        #    port_table['name'] = device_name
        worksheet_names.append(port_table[0]['name'])
        print(f'writing port/interface table to excel file for {device_name}...')
        tables.append([port_table])

    print('saving excel file to migration.xlsx')
    excel_util.write_tables_to_excel_worksheets('migration.xlsx',worksheet_names,tables)