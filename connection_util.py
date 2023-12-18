import paramiko
from netmiko import ConnectHandler
import yaml
import os

def get_hostname(os_name:str, sshclient) -> str:
    '''
    Query the host for its hostname. Returns the string without the trailing newline.
    param:
        sshclient is either paramiko.client.SSHClient or netmiko.ConnectHandler
    '''
    if os_name == 'aos-cx':
        _stdin, _stdout, _stderr = sshclient.exec_command('show host')
        return _stdout.read().decode().strip()
    elif os_name == 'aos-s':
        prompt = sshclient.find_prompt()
        return prompt[:-1]
    else:
        raise ValueError('OS currently not supported')

def write_command_outputs_to_file(command_outputs:list[list[str]], show_files_path:str, os_name:str, hostname:str) -> None:
    '''
    Takes all the outputs from the commands and writes them to the file at show_files_path/os_name/hostname.txt
    '''
    file_lines = []
    for output in command_outputs:
        for line in output:
            file_lines.append(line+'\n')
    os_fullpath = os.path.join(show_files_path, os_name)
    if not os.path.exists(os_fullpath):
        print(f'{os_name} directory not found in the show_files directory. Creating {os_name} directory.')
        os.mkdir(os_fullpath)
    host_output_path = os.path.join(os_fullpath, f'{hostname}.txt')
    with open(host_output_path, mode = 'w', encoding='utf-8', errors="replace") as f:
        print(f'Writing output for {hostname} to show_files/{os_name}/{hostname}.txt')
        f.writelines(file_lines)
    print('File saved successfully.')
    return

def gather_information_from_hosts(show_commands:dict[str,list[str]]):
    '''
    Connect to all the hosts in the hosts file and collect information from them.
    The three commands ran against each host are show mac-address, show vlan and show arp.
    The output for each host is written to show_files/HOST_OS/HOSTNAME.txt
    The show_commands dictionary contains a list of show commands to perform against each OS type.
    '''
    print('Discovered hosts.yml file. Processing hosts.')
    with open('./hosts.yml', 'r') as hosts_file:
        supported_os = {
            'aos-cx' : {
                'module' : 'paramiko',
            },
            'aos-s' : {
                'module' : 'netmiko',
                'netmiko-type' : 'aruba_osswitch'
            }
        }
        hosts = yaml.safe_load(hosts_file)['hosts']
        cwd = os.getcwd()
        show_files_path = os.path.join(cwd, 'show_files')
        if not os.path.exists(show_files_path):
            print(f'No show_files directory found. Creating {show_files_path}.')
            os.mkdir(show_files_path)
        for os_name,hosts_values in hosts.items():
            if os_name in supported_os:
                for host in hosts_values:
                    print(f'Attempting to ssh into {host["host"]}')
                    fqdn, username, password = host['host'], host['credentials']['username'], host['credentials']['password']
                    try:
                        if supported_os[os_name]['module'] == 'paramiko':
                            client = paramiko.client.SSHClient()
                            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            client.connect(fqdn, username=username, password=password, look_for_keys=False)
                            print(f'Successfully connected to {host["host"]}')
                            print('Getting hostname')
                            hostname = get_hostname(os_name, client)
                            commands = show_commands[os_name]
                            command_outputs = []
                            for command in commands:
                                print(f'Sending command {command}')
                                _stdin, _stdout, _stderr = client.exec_command(command)
                                command_outputs.append(_stdout.read().decode().split('\n'))
                            write_command_outputs_to_file(command_outputs, show_files_path, os_name, hostname)
                            client.close()
                        elif supported_os[os_name]['module'] == 'netmiko':
                            connection = ConnectHandler(device_type=supported_os[os_name]['netmiko-type'], host=fqdn, username=username, password=password)
                            print(f'Successfully connected to {host["host"]}')
                            print('Getting hostname')
                            hostname = get_hostname(os_name, connection)
                            commands = show_commands[os_name]
                            command_outputs = []
                            for command in commands:
                                print(f'Sending command {command}')
                                command_outputs.append(connection.send_command(command).split('\n'))
                            write_command_outputs_to_file(command_outputs, show_files_path, os_name, hostname)
                            connection.disconnect()
                    except:
                        print(f'Problem SSHing into host. Check host details. Skipping host {fqdn}.')
            else:
                print(f'Automated SSH not currently supported for {os_name}. Upload the configuration files manually to the show_files folder.')