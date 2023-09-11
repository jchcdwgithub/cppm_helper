import data_util
import os
import connection_util
import excel_util
import file_util

def main():
    cwd = os.getcwd()
    hosts_file = os.path.join(cwd, 'hosts.yml')
    if os.path.exists(hosts_file):
        connection_util.gather_information_from_hosts()

    config_files_directory = './show_files'
    if not os.path.exists(config_files_directory):
        raise FileNotFoundError('There is no show_files directory to process. Add the configuration files under the correct os folders to the show_files folder and run the script again.')
    directory_files = os.listdir(config_files_directory)
    extracted_tables = {}
    for os_name in directory_files:
        template_files = {
            'sh_mac_address':f'./templates/{os_name}/sh_mac_address.template',
            'sh_arp':f'./templates/{os_name}/sh_arp.template',
            'sh_vlan':f'./templates/{os_name}/sh_vlan.template'
            }
        os_directory = os.path.join(config_files_directory,os_name)
        os_config_files = os.listdir(os_directory)
        if len(os_config_files) != 0:
            extracted_tables[os_name] = []
            for os_config_file in os_config_files:
                config_file = os.path.join(os_directory,os_config_file)
                config_tables = file_util.extract_tables_from_config_file(template_files, config_file, os_config_file)
                if not 'sh_mac_address' in config_tables:
                    print(f'No information could be extracted for the show mac-address command in the file {os_config_file}. This is required information. Skipping this file.')
                else:
                    extracted_tables[os_name].append(config_tables) 
        else:
            print(f'found a folder for {os_name} platform but the folder is empty. Skipping processing...')

    mac_vendors = data_util.create_mac_vendors_dict_from_mac_oui_csv()

    main_mac_tables = []
    vlan_tables = []
    vendor_catalogue_tables = []
    worksheet_names = []
    table_sets = []

    print('Creating tables from parsed information.')
    for os_name,hosts in extracted_tables.items():
        for host in hosts:

            host_first_column_tables = []
            host_second_column_tables = []

            hostname = host['hostname']
            print(f'Creating main MAC table for {hostname}')
            host_devices = data_util.add_information_to_devices_from_tables(host,mac_vendors)
            host['devices'] = host_devices

            host_main_mac_table = data_util.create_host_main_mac_tables(host)
            host_second_column_tables.append(host_main_mac_table)
            main_mac_tables.append(host_main_mac_table)

            if 'sh_vlan' in host:
                print(f'Creating VLAN table for {hostname}')
                host_vlan_table = data_util.create_host_vlan_table(host)
            else:
                print(f'Creating VLAN table from sh_mac_address command for {hostname}')
                host_vlan_table = data_util.create_host_vlan_table_from_sh_mac_address_info(host)
            vlan_tables.append(host_vlan_table)
            host_first_column_tables.append(host_vlan_table)

            print(f'Cataloging devices by vendor for {hostname}')
            host_vendor_catalogue_table = data_util.create_host_vendor_catalogue_table(host)
            vendor_catalogue_tables.append(host_vendor_catalogue_table)
            host_first_column_tables.append(host_vendor_catalogue_table)

            worksheet_names.append(host['hostname'])

            print(f'Saving tables to worksheet for {hostname}')
            table_sets.append([host_first_column_tables, host_second_column_tables])

    first_column_tables = []
    print('Aggregating VLAN information across all hosts.')
    combined_vlan_table = data_util.combine_vlan_tables(vlan_tables)
    first_column_tables.append(combined_vlan_table)

    print('Aggregating vendor to device catalog across all hosts.')
    combined_vendor_catalogue_tables = data_util.combine_vendor_catalogue_tables(vendor_catalogue_tables)
    first_column_tables.append(combined_vendor_catalogue_tables)

    worksheet_names.append('Overview')

    second_column_tables = main_mac_tables

    table_sets.append([first_column_tables,second_column_tables])

    print('Writing all information to excel workbook.')
    excel_util.write_tables_to_excel_worksheets('output.xlsx', worksheet_names, table_sets)
    print('Done.')
    print(f'The excel file can be found at the root directory named output.xlsx')

if __name__ == "__main__":
    main()