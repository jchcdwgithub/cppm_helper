import file_util
import excel_util
import data_util
import os

supported_oses = ['aos-s']
cwd = os.getcwd()
device_names = []
device_names_populated = False
templates_folder = os.path.join(cwd, 'templates')
host_index = 1
for supported_os in supported_oses:
    aos_s_templates_folder = os.path.join(templates_folder, supported_os)
    templates = ['sh_int_status.template', 'sh_run_int.template','sh_lldp_in_re_de.template', 'sh_cdp_ne_de.template', 'sh_run_vlans.template']
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
    
    vlan_tables = []
    worksheet_names.append('Layer 2 & 3')
    tables.append(vlan_tables)

    for device_name, device in zip(device_names, results):
        print(f'aggregating show information for {device_name}...')
    #create individual device port tables
        print(f'aggregating L2/3 information into tables...')
        device_vlans = {}
        sh_run_vlans = device[4]
        vlan_data = sh_run_vlans[1]
        vlan_headers = sh_run_vlans[0]
        headers_to_include = ['VLAN_ID', 'VLAN_NAME']
        for vlan in vlan_data:
            current_vlan = {}
            for header,attribute in zip(vlan_headers, vlan):
                if header == 'VLAN_ID':
                    device_vlans[attribute] = current_vlan
                elif header in headers_to_include:
                    current_vlan[header] = attribute
        converted_ip_addresses = data_util.convert_vlan_ip_subnet_to_slash_notation(sh_run_vlans)
        vlan_table = {}
        vlan_table['headers'] = headers_to_include
        vlan_table['data'] = device_vlans
        vlan_table['name'] = device_name
        
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
                
        for output,output_data in vlan_outputs.items():
            output_headers = output_data['parsed_data'][0]
            output_info = output_data['parsed_data'][1]
            output_new_headers = output_data['new_headers']
            data_util.update_new_header_indices(output_headers, output_new_headers)
            data_util.add_new_headers_to_parsed_data(vlan_table, output_info, output_new_headers, 0)
            data_util.fill_data_with_empty_values(vlan_table, output_new_headers)
        
        data_table = data_util.convert_dictionary_to_table_structure(vlan_table)
        vlan_table['data'] = data_table

        vlan_tables.append([vlan_table])

        ports = {}
        sh_run_int_data = device[1]
        port_data = sh_run_int_data[1]
        port_headers = sh_run_int_data[0]
        for port in port_data:
            current_port = {}
            for header,attribute in zip(port_headers,port):
                if header == 'INTERFACE':
                    ports[attribute] = current_port 
                else:
                    current_port[header] = attribute

        port_table = {}
        port_table['headers'] = port_headers
        port_table['data'] = ports

        outputs = {}
        outputs['cdp_neighbor'] = {
            'parsed_data' : device[3],
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
            }
        outputs['lldp_neighbors'] = {
            'parsed_data' : device[2],
            'new_headers' : {
                'SYSTEM_NAME' : {
                    'index' : 0,
                    'new_name' : 'NEIGHBOR_NAME'
                }
            }   
        }
        outputs['sh_int_status'] = {
            'parsed_data' : device[0],
            'new_headers' : {
                h : {
                    'index' : i,
                    'new_name' : h
                } for i,h in enumerate(device[0][0][2:len(device[0][0])-2], start=2)
            }
        }

        for output,output_data in outputs.items():
            output_headers = output_data['parsed_data'][0]
            output_info = output_data['parsed_data'][1]
            output_new_headers = output_data['new_headers']
            data_util.update_new_header_indices(output_headers, output_new_headers)
            data_util.add_new_headers_to_parsed_data(port_table, output_info, output_new_headers, 0)
            data_util.fill_data_with_empty_values(port_table, output_new_headers)

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