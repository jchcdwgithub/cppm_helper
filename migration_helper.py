import file_util
import excel_util
import data_util
import os

supported_oses = ['aos-s']
cwd = os.getcwd()
templates_folder = os.path.join(cwd, 'templates')
for supported_os in supported_oses:
    aos_s_templates_folder = os.path.join(templates_folder, supported_os)
    templates = ['sh_int_status.template', 'sh_run_int.template','sh_lldp_in_re_de.template', 'sh_cdp_ne_de.template']
    results = []
    worksheet_names = []
    tables = []
    show_file_path = os.path.join(cwd,'show_files')
    show_files_os_path = os.path.join(show_file_path, supported_os)
    show_files = os.listdir(show_files_os_path)
    current_device = []
    for show_file in show_files:
        show_filepath = os.path.join(show_files_os_path, show_file)
        for template in templates:
            template_filepath = os.path.join(aos_s_templates_folder, template)
            current_device.append(file_util.extract_table_from_config_file(template_filepath, show_filepath))
        new_table = data_util.remove_trunk_from_port_name(current_device[0])
        current_device[0] = new_table
        results.append(current_device)

    for device in results:

    #create individual device port tables
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
        port_table['name'] = 'host1'
        worksheet_names.append(port_table['name'])
        tables.append([[port_table]])

    excel_util.write_tables_to_excel_worksheets('migration.xlsx',worksheet_names,tables)