import file_util
import excel_util
import data_util
import connection_util
import os
import copy
import data_structures

def main():
    supported_oses = ['aos-cx', 'aos-s', 'ios-xe', 'nx-os', 'ios']
    cwd = os.getcwd()
    hosts_file = os.path.join(cwd, 'hosts.yml')
    if os.path.exists(hosts_file):
        connection_util.gather_information_from_hosts(data_structures.show_commands)
    templates_folder = os.path.join(cwd, 'templates')
    for supported_os in supported_oses:
        aos_s_templates_folder = os.path.join(templates_folder, supported_os)
        results = []
        worksheet_names = []
        tables = []
        device_names = []
        device_names_populated = False
        show_file_path = os.path.join(cwd,'show_files')
        show_files_os_path = os.path.join(show_file_path, supported_os)
        if os.path.exists(show_files_os_path):
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
                        if hostname == '':
                            hostname = data_util.extract_hostname_from_show_file(show_file)
                        device_names.append(hostname)

            worksheet_names.append('Overview')

            dns_all_systems = {}
            dns_systems_table = {}
            overview_tables = []
            overview_first_column = []

            ip_helper_all_systems = {}
            ip_helper_systems_table = {}

            ntp_ip_all_systems = {}
            ntp_ip_systems_table = {}

            radius_all_systems = {}
            radius_systems_table = {}

            snmp_all_systems = {}
            snmp_systems_table = {}
    
            for device_name, device in zip(device_names, results):
                print(f'gathering DNS information for {device_name}...')
                dns_headers_to_include = ['DNS_IP']
                data_util.create_base_table(device[data_structures.os_templates[supported_os].index('ip_dns_server_address.template')], dns_headers_to_include,'DNS_IP', dns_all_systems)

                print(f'gathering IP helper address information for {device_name}...')
                ip_helper_headers_to_include = ['VLAN_ID', 'IP_HELPER_ADDRESS']
                if supported_os == 'aos-cx':
                    data_util.create_base_table(device[data_structures.os_templates[supported_os].index('sh_run_int_vlans.template')], ip_helper_headers_to_include, 'VLAN_ID', ip_helper_all_systems)
                elif supported_os == 'aos-s':
                    data_util.create_base_table(device[data_structures.os_templates[supported_os].index('sh_run_vlans.template')], ip_helper_headers_to_include, 'VLAN_ID',ip_helper_all_systems)
                elif supported_os == 'ios-xe':
                    data_util.create_base_table(device[data_structures.os_templates[supported_os].index('sh_run_int_vlans.template')], ip_helper_headers_to_include, 'VLAN_ID',ip_helper_all_systems)
                elif supported_os == 'nx-os':
                    data_util.create_base_table(device[data_structures.os_templates[supported_os].index('sh_run_int_vlans.template')], ip_helper_headers_to_include, 'VLAN_ID',ip_helper_all_systems)
                elif supported_os == 'ios':
                    data_util.create_base_table(device[data_structures.os_templates[supported_os].index('sh_run_ip_helper.template')], ip_helper_headers_to_include, 'VLAN_ID',ip_helper_all_systems)

                print(f'gathering NTP information for {device_name}...')
                ntp_ip_headers_to_include = ['NTP_SERVER_IP']
                data_util.create_base_table(device[data_structures.os_templates[supported_os].index('ntp_server_ip.template')], ntp_ip_headers_to_include, 'NTP_SERVER_IP', ntp_ip_all_systems)

                print(f'gathering RADIUS information for {device_name}...')
                radius_headers_to_include = ['RADIUS_HOST']
                data_util.create_base_table(device[data_structures.os_templates[supported_os].index('run_radius.template')], radius_headers_to_include, 'RADIUS_HOST', radius_all_systems)

                print(f'gathering SNMP information for {device_name}...')
                snmp_headers_to_include = ['SNMP_SERVER_IP']
                data_util.create_base_table(device[data_structures.os_templates[supported_os].index('snmp_server_host.template')], snmp_headers_to_include, 'SNMP_SERVER_IP', snmp_all_systems)

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
            if len(helper_ips) > 0:
                ip_helper_systems_table = data_util.create_excel_printable_table('DHCP', helper_ips, ['IP_HELPER_ADDRESS'], convert_table=False)
                overview_first_column.append(ip_helper_systems_table)

            ntp_ip_systems_table = data_util.create_excel_printable_table('NTP', ntp_ip_all_systems, ['NTP_SERVER_IP'])
            overview_first_column.append(ntp_ip_systems_table)

            radius_systems_table = data_util.create_excel_printable_table('RADIUS', radius_all_systems, ['RADIUS_HOST'])
            overview_first_column.append(radius_systems_table)

            snmp_systems_table = data_util.create_excel_printable_table('SNMP', snmp_all_systems, ['SNMP_SERVER_IP'])
            overview_first_column.append(snmp_systems_table)

            overview_tables.append(overview_first_column)

            all_systems = {}

            for device_name, device in zip(device_names, results):
                system_table = copy.deepcopy(data_structures.os_tables[supported_os]['system_table'])
                if all_systems == {}:
                    all_systems = data_util.create_column_ds(system_table, device)
                    current_device_headers = all_systems[0]['headers']
                    sys_name_index = current_device_headers.index('SYSTEM_NAME')
                    current_device_data = all_systems[0]['data']
                    for data_row in current_device_data:
                        data_row[sys_name_index] = device_name
                else:
                    current_device_info = data_util.create_column_ds(system_table, device)
                    data_rows = current_device_info[0]['data']
                    current_device_headers = all_systems[0]['headers']
                    sys_name_index = current_device_headers.index('SYSTEM_NAME')
                    current_device_data = all_systems[0]['data']
                    for data_row in data_rows:
                        data_row[sys_name_index] = device_name
                        all_systems[0]['data'].append(data_row)

            overview_tables.append(all_systems)
            tables.append(overview_tables)

            all_vlans = set()
            for device in results:
                if supported_os == 'ios':
                    device_vlans = device[data_structures.os_templates[supported_os].index('sh_vlan.template')]
                else:
                    device_vlans = device[data_structures.os_templates[supported_os].index('sh_run_vlans.template')]
                device_vlan_headers = device_vlans[0]
                device_vlan_data = device_vlans[1]
                vlan_id_index = device_vlan_headers.index('VLAN_ID')
                for vlan in device_vlan_data:
                    vlan_id = vlan[vlan_id_index]
                    if not vlan_id in all_vlans:
                        all_vlans.add(vlan_id)

            for device in results:
                if supported_os == 'ios':
                    device_vlans = device[data_structures.os_templates[supported_os].index('sh_vlan.template')]
                else:
                    device_vlans = device[data_structures.os_templates[supported_os].index('sh_run_vlans.template')]
                device_vlan_headers = device_vlans[0]
                device_vlan_data = device_vlans[1]
                vlan_id_index = device_vlan_headers.index('VLAN_ID')
                device_vlans = set()
                for vlan in device_vlan_data:
                    vlan_id = vlan[vlan_id_index]
                    device_vlans.add(vlan_id)
                for vlan in all_vlans:
                    if not vlan in device_vlans:
                        vlan_row = [vlan]
                        for _ in device_vlan_headers[1:]:
                            vlan_row.append('')
                        device_vlan_data.append(vlan_row)
                device_vlan_data.sort(key=lambda x : int(x[0]))

            vlan_tables = []
            worksheet_names.append('Layer 2 & 3')
            tables.append(vlan_tables)

            for device_name, device in zip(device_names, results):

                print(f'aggregating L2/3 information into tables...')
                current_table = data_util.create_column_ds(copy.deepcopy(data_structures.os_tables[supported_os]['L2/L3'][0]), device)
                current_table[0]['name'] = device_name
                vlan_tables.append(current_table)

                if supported_os == 'aos-cx':
                   sh_run_int_index = data_structures.os_templates[supported_os].index('sh_run_int.template')
                   sh_int_lag_table = device[data_structures.os_templates[supported_os].index('sh_run_int_lag.template')]
                   sh_int_table = device[data_structures.os_templates[supported_os].index('sh_run_int.template')]
                   merged_table = data_util.merge_tables_into_one_table([sh_int_lag_table, sh_int_table])
                   device[sh_run_int_index] = merged_table

                device_port_table = copy.deepcopy(data_structures.os_tables[supported_os]['device_port_table'])
                device_port_table[0]['table_name'] = device_name
                if supported_os == 'ios-xe':
                    tables_to_convert = ['sh_cdp_ne_de.template', 'sh_run_int.template', 'sh_run_int_lag.template']
                    for current_table in tables_to_convert:
                        current_table_to_convert = device[data_structures.os_templates[supported_os].index(current_table)]
                        data_util.truncate_interface_names(current_table_to_convert, supported_os)
                if supported_os == 'ios':
                    tables_to_convert = ['sh_cdp_ne_de.template', 'sh_run_int.template', 'sh_run_int_lag.template']
                    for current_table in tables_to_convert:
                        current_table_to_convert = device[data_structures.os_templates[supported_os].index(current_table)]
                        data_util.truncate_interface_names(current_table_to_convert, supported_os)
                elif supported_os == 'nx-os':
                    tables_to_convert = ['sh_run_int.template', 'sh_run_int.template', 'sh_run_int_lag.template', 'sh_cdp_ne_de.template']
                    for current_table in tables_to_convert:
                        current_table_to_convert = device[data_structures.os_templates[supported_os].index(current_table)]
                        data_util.truncate_interface_names(current_table_to_convert, supported_os)

                port_table = data_util.create_column_ds(device_port_table, device)
                worksheet_names.append(port_table[0]['name'])
                print(f'writing port/interface table to excel file for {device_name}...')
                tables.append([port_table])

            print(f'saving excel file to migration-{supported_os}.xlsx')
            excel_util.write_tables_to_excel_worksheets(f'migration-{supported_os}.xlsx',worksheet_names,tables)

if __name__ == "__main__":
    main()