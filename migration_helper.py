import file_util
import excel_util
import data_util
import os
import copy
import data_structures

supported_oses = ['aos-cx','aos-s']
cwd = os.getcwd()
templates_folder = os.path.join(cwd, 'templates')
host_index = 1
for supported_os in supported_oses:
    aos_s_templates_folder = os.path.join(templates_folder, supported_os)
    results = []
    worksheet_names = []
    tables = []
    device_names = []
    device_names_populated = False
    show_file_path = os.path.join(cwd,'show_files')
    show_files_os_path = os.path.join(show_file_path, supported_os)
    show_files = os.listdir(show_files_os_path)
    for show_file in show_files:
        show_filepath = os.path.join(show_files_os_path, show_file)
        print(f'Parsing information in file {show_file}...')
        current_device = []
        for template in data_structures.os_templates[supported_os]:
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
        dns_table = data_util.create_base_table(device[data_structures.os_templates[supported_os].index('ip_dns_server_address.template')], dns_headers_to_include,'DNS_IP', dns_all_systems)

        print(f'gathering IP helper address information for {device_name}...')
        ip_helper_headers_to_include = ['VLAN_ID', 'IP_HELPER_ADDRESS']
        ip_helper_table = data_util.create_base_table(device[data_structures.os_templates[supported_os].index('sh_run_vlans.template')], ip_helper_headers_to_include, 'VLAN_ID',ip_helper_all_systems)

        print(f'gathering NTP information for {device_name}...')
        ntp_ip_headers_to_include = ['NTP_SERVER_IP']
        ntp_ip_table = data_util.create_base_table(device[data_structures.os_templates[supported_os].index('ntp_server_ip.template')], ntp_ip_headers_to_include, 'NTP_SERVER_IP', ntp_ip_all_systems)

        print(f'gathering RADIUS information for {device_name}...')
        radius_headers_to_include = ['RADIUS_HOST']
        radius_table = data_util.create_base_table(device[data_structures.os_templates[supported_os].index('run_radius.template')], radius_headers_to_include, 'RADIUS_HOST', radius_all_systems)

        print(f'gathering SNMP information for {device_name}...')
        snmp_headers_to_include = ['SNMP_SERVER_IP']
        snmp_table = data_util.create_base_table(device[data_structures.os_templates[supported_os].index('snmp_server_host.template')], snmp_headers_to_include, 'SNMP_SERVER_IP', snmp_all_systems)

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
        system_table = copy.deepcopy(data_structures.os_tables[supported_os]['system_table'])
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
        device_vlans = device[data_structures.os_templates[supported_os].index('sh_run_vlans.template')]
        device_vlan_headers = device_vlans[0]
        device_vlan_data = device_vlans[1]
        vlan_id_index = device_vlan_headers.index('VLAN_ID')
        for vlan in device_vlan_data:
            vlan_id = vlan[vlan_id_index]
            if not vlan_id in all_vlans:
                all_vlans.add(vlan_id)

    for device in results:
        device_vlans = device[data_structures.os_templates[supported_os].index('sh_run_vlans.template')]
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
        current_table = data_util.create_column_ds(data_structures.os_tables[supported_os]['L2/L3'][0], device)
        current_table[0]['name'] = device_name
        vlan_tables.append(current_table)

        device_port_table = copy.deepcopy(data_structures.os_tables[supported_os]['device_port_table'])
        device_port_table[0]['table_name'] = device_name

        port_table = data_util.create_column_ds(device_port_table, device)
        worksheet_names.append(port_table[0]['name'])
        print(f'writing port/interface table to excel file for {device_name}...')
        tables.append([port_table])

    print(f'saving excel file to migration-{supported_os}.xlsx')
    excel_util.write_tables_to_excel_worksheets(f'migration-{supported_os}.xlsx',worksheet_names,tables)