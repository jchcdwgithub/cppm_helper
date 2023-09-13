import paramiko
import yaml

def get_hostname(os_name:str, sshclient:paramiko.client.SSHClient) -> str:
    '''
    Query the host for its hostname. Returns the string without the trailing newline.
    '''
    if os_name == 'aos-cx':
        _stdin, _stdout, _stderr = sshclient.exec_command('show host')
        return _stdout.read().decode().strip()
    else:
        raise ValueError('OS currently not supported')

def gather_information_from_hosts():
    '''
    Connect to all the hosts in the hosts file and collect information from them.
    The three commands ran against each host are show mac-address, show vlan and show arp.
    The output for each host is written to show_files/HOST_OS/HOSTNAME.txt
    '''
    print('Discovered hosts.yml file. Processing hosts.')
    with open('./hosts.yml', 'r') as hosts_file:
        supported_os = ['aos-cx']
        hosts = yaml.safe_load(hosts_file)['hosts']
        for os_name,hosts_values in hosts.items():
            if os_name in supported_os:
                for host in hosts_values:
                    print(f'Attempting to ssh into {host["host"]}')
                    fqdn, username, password = host['host'], host['credentials']['username'], host['credentials']['password']
                    client = paramiko.client.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    try:
                        client.connect(fqdn, username=username, password=password, look_for_keys=False)
                        print(f'Successfully connected to {host["host"]}')
                        print('Getting hostname')
                        hostname = get_hostname(os_name, client)
                        commands = ['show mac-address', 'show vlan', 'show arp']
                        command_outputs = []
                        for command in commands:
                            print(f'Sending command {command}')
                            _stdin, _stdout, _stderr = client.exec_command(command)
                            command_outputs.append(_stdout.read().decode().split('\n'))
                        file_lines = []
                        for output in command_outputs:
                            for line in output:
                                file_lines.append(line+'\n')
                        with open(f'./show_files/{os_name}/{hostname}.txt', 'w') as f:
                            print(f'Writing output for {hostname} to show_files/{os_name}/{hostname}.txt')
                            f.writelines(file_lines)
                        client.close()
                    except:
                        print(f'Problem SSHing into host. Check host details. Skipping host {fqdn}.')
            else:
                print(f'Automated SSH not currently supported for {os_name}. Upload the configuration files manually to the show_files folder.')