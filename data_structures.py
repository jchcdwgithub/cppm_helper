os_templates = {
    'aos-s' : [
        'sh_int_status.template',
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
        'sh_trunks.template',
    ],
    'aos-cx' : [
        'ntp_server_ip.template',
        'sh_cdp_ne_de.template',
        'sh_lldp_in_re_de.template',
        'sh_module.template',
        'sh_run_int_vlans.template',
        'sh_run_int.template',
        'sh_run_int_lag.template',
        'sh_run_vlans.template',
        'sh_system.template',
        'run_radius.template',
        'snmp_server_host.template',
        'snmp_community.template',
        'ip_dns_server_address.template',
        'ip_dns_domain_name.template',
        'sh_int_status.template',
    ]
}

os_tables = {
    'aos-s' : {
        'device_port_table' : 
        [
            {
                'table_name' : '',
                'base_table' : {
                    'base_table_index' : os_templates['aos-s'].index('sh_run_int.template'),
                    'headers_to_include' : ['INTERFACE', 'NAME', 'UNTAGGED_VLAN', 'TAGGED_VLAN'],
                    'key': 'INTERFACE'
                },
                'parsed_info_to_add': [
                    {
                        'table_name' : 'sh_cdp_ne_de',
                        'table_index' : os_templates['aos-s'].index('sh_cdp_ne_de.template'),
                        'headers_to_add' : [
                            ('IP_ADDRESS', 'NEIGHBOR_IP'),
                            ('PLATFORM', 'NEIGHBOR_PLATFORM')
                        ]
                    },
                    {
                        'table_name' : 'lldp_neighbors',
                        'table_index' : os_templates['aos-s'].index('sh_lldp_in_re_de.template'),
                        'headers_to_add' : [
                            ('SYSTEM_NAME', 'NEIGHBOR_NAME')
                        ]
                    },
                    {
                        'table_name' : 'sh_int_status',
                        'table_index' : os_templates['aos-s'].index('sh_int_status.template'),
                        'headers_to_add' : [
                            ('STATUS', 'STATUS'),
                            ('CONFIG_MODE', 'CONFIG_MODE'),
                            ('SPEED', 'SPEED'),
                            ('TYPE', 'TYPE'),
                        ]
                    },
                    {
                        'table_name' : 'sh_trunks',
                        'table_index' : os_templates['aos-s'].index('sh_trunks.template'),
                        'headers_to_add' : [
                            ('GROUP', 'TRUNK'),
                            ('LACP', 'LACP')
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
                            'LACP',
                            'TAGGED_VLAN',
                            'UNTAGGED_VLAN'
                            ],
                'convert_table' : True
            }
        ],
        'L2/L3' : [
            [
                {
                    'table_name' : '',
                    'base_table' : {
                        'base_table_index' : os_templates['aos-s'].index('sh_run_vlans.template'),
                        'headers_to_include' : ['VLAN_ID', 'VLAN_NAME', 'IP_ADDRESS'],
                        'key' : 'VLAN_ID'
                    },
                    'final_headers' : ['VLAN_ID', 'VLAN_NAME', 'IP_ADDRESS'],
                    'convert_table' : True
                }
            ]
        ],
        'system_table' :
        [
            {
                'table_name' : 'system_info',
                'base_table' : {
                    'base_table_index' : os_templates['aos-s'].index('sh_system.template'),
                    'headers_to_include' : ['SYSTEM_NAME', 'SOFTWARE_VERSION', 'SERIAL_NUMBER'],
                    'key' : 'SERIAL_NUMBER'
                },
                'parsed_info_to_add' : [
                    {
                        'table_name' : 'sh_module',
                        'table_index' : os_templates['aos-s'].index('sh_module.template'),
                        'headers_to_add' : [
                            ('CHASSIS_MODEL', 'CHASSIS_MODEL')
                        ],
                    }
                ],
                'final_headers' : ['LOCATION', 'SUB_LOCATION', 'SYSTEM_NAME', 'MGMT_IP', 'MGMT_SOURCE', 'CHASSIS_MODEL', 'SERIAL_NUMBER', 'SOFTWARE_VERSION'],
                'convert_table' : True,
                'matched_parameter_index' : 1
            }
        ],
    },
    'aos-cx' : {
        'device_port_table' :
        [
            {
                'table_name' : '',
                'base_table' : {
                    'base_table_index' : os_templates['aos-cx'].index('sh_int_status.template'),
                    'headers_to_include' : ['INTERFACE', 'STATUS', 'CONFIG_MODE', 'SPEED', 'TYPE'],
                    'key': 'INTERFACE'
                },
                'parsed_info_to_add': [
                    {
                        'table_name' : 'lldp_neighbors',
                        'table_index' : os_templates['aos-cx'].index('sh_lldp_in_re_de.template'),
                        'headers_to_add' : [
                            ('SYSTEM_NAME', 'NEIGHBOR_NAME'),
                            ('SYSTEM_DESCRIPTION', 'NEIGHBOR_DESCRIPTION')
                        ]
                    },
                    {
                        'table_name' : 'sh_run_int',
                        'table_index' : os_templates['aos-cx'].index('sh_run_int.template'),
                        'headers_to_add' : [
                            ('NATIVE_VLAN', 'NATIVE_VLAN'),
                            ('TAGGED_VLAN', 'TAGGED_VLAN'),
                            ('NAME', 'NAME'),
                        ]
                    },
                    {
                        'table_name' : 'sh_run_int_lag.template',
                        'table_index' : os_templates['aos-cx'].index('sh_run_int_lag.template'),
                        'headers_to_add' : [
                            ('LAG', 'LAG')
                        ]
                    }
                ],
                'final_headers' : [
                    'INTERFACE',
                    'NAME',
                    'NEIGHBOR_NAME',
                    'NEIGHBOR_DESCRIPTION',
                    'STATUS',
                    'CONFIG_MODE',
                    'SPEED',
                    'TYPE',
                    'LAG',
                    'NATIVE_VLAN',
                    'TAGGED_VLAN'
                ],
                'convert_table' : True
            }
        ],
        'L2/L3' : [
            [
                {
                    'table_name' : '',
                    'base_table' : {
                        'base_table_index' : os_templates['aos-cx'].index('sh_run_vlans.template'),
                        'headers_to_include' : ['VLAN_ID', 'VLAN_NAME'],
                        'key' : 'VLAN_ID'
                    },
                    'parsed_info_to_add' : [
                        {
                            'table_name' : 'sh_run_int_vlans',
                            'table_index' : os_templates['aos-cx'].index('sh_run_int_vlans.template'),
                            'headers_to_add' : [
                                ('IP_ADDRESS', 'IP_ADDRESS')
                            ]
                        }
                    ],
                    'final_headers' : ['VLAN_ID', 'VLAN_NAME', 'IP_ADDRESS'],
                    'convert_table' : True
                }
            ]
        ],
        'system_table' :
        [
            {
                'table_name' : 'system_info',
                'base_table' : {
                    'base_table_index' : os_templates['aos-cx'].index('sh_system.template'),
                    'headers_to_include' : ['SYSTEM_NAME', 'SOFTWARE_VERSION', 'SERIAL_NUMBER'],
                    'key' : 'SERIAL_NUMBER'
                },
                'parsed_info_to_add' : [
                    {
                        'table_name' : 'sh_module',
                        'table_index' : os_templates['aos-cx'].index('sh_module.template'),
                        'headers_to_add' : [
                            ('CHASSIS_MODEL', 'CHASSIS_MODEL')
                        ],
                    }
                ],
                'final_headers' : ['LOCATION', 'SUB_LOCATION', 'SYSTEM_NAME', 'MGMT_IP', 'MGMT_SOURCE', 'CHASSIS_MODEL', 'SERIAL_NUMBER', 'SOFTWARE_VERSION'],
                'convert_table' : True,
                'matched_parameter_index' : 1
            }
        ],
    },
}

show_commands = {
    'aos-s' : [
        'show run',
        'show cdp ne de',
        'show cdp ne',
        'show lldp in re de',
        'show inter status',
        'show system',
        'show module',
        'show mac-address',
        'show arp',
        'show trunks',
        'show lacp',
        'show ip route',
        'show power-over-ethernet br',
        'show spanning-tree',
        'show spanning-tree config',
        'show spanning-tree inconsistent-ports',
        'show flash',
        'show vlans',
        'show name',
        'show inter br',
        'show version',
    ],
    'aos-cx' : [
        'show run',
        'show version',
        'show lldp ne',
        'show lldp ne de',
        'show mac-address',
        'show arp',
        'show int br',
        'show lacp aggregates',
        'show ip route',
        'show ip route all-vrfs',
        'show ip ospf',
        'show ip ospf routes',
        'show ip ospf neighbors',
        'show ip ospf neighbors detail',
        'show ip ospf statistics',
        'show spanning-tree',
        'show spanning-tree detail',
        'show spanning-tree inconsistent-ports',
        'show spanning-tree summary root',
        'show power-over-ethernet',
        'show power-over-ethernet br',
        'show system',
        'show module',
        'show cdp ne',
        'show vlan',
    ]
}