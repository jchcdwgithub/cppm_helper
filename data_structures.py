os_templates = {
    'aos-s' : [
        'sh_int_status.template',
        'sh_run_int.template',
        'sh_lldp_in_re_de.template',
        'sh_cdp_ne_de.template',
        'sh_run_vlans.template',
        'sh_run_vlans_id.template',
        'sh_run_ip_helper.template',
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
        'sh_run_int_ip_helper.template',
        'sh_run_int.template',
        'sh_run_int_trunk.template',
        'sh_run_int_lag.template',
        'sh_interfaces.template',
        'sh_run_vlans.template',
        'sh_system.template',
        'run_radius.template',
        'snmp_server_host.template',
        'snmp_community.template',
        'ip_dns_server_address.template',
        'ip_dns_domain_name.template',
        'sh_int_status.template',
    ],
    'ios-xe' : [
        'sh_cdp_ne_de.template',
        'sh_int_desc.template',
        'sh_int_stats.template',
        'sh_etherchannel_sum.template',
        'sh_module.template',
        'sh_run_vlans.template',
        'sh_vlans.template',
        'sh_run_int.template',
        'sh_run_int_lag.template',
        'sh_run_int_vlans.template',
        'sh_run_dns.template',
        'ip_dns_server_address.template',
        'sh_run_int_lo.template',
        'sh_run_hostname.template',
        'snmp_server_host.template',
        'run_radius.template',
        'ntp_server_ip.template',
        'sh_arp.template',
        'sh_mac_address.template',
        'sh_run_domain_name.template'
    ],
    'nx-os' : [
        'sh_cdp_ne_de.template',
        'sh_mac_address.template',
        'sh_int_desc_eth.template',
        'sh_int_stats.template',
        'sh_module.template',
        'sh_module_mac_serial.template',
        'sh_run_hostname.template',
        'ip_dns_server_address.template',
        'sh_run_domain_name.template',
        'ntp_server_ip.template',
        'sh_run_vlans.template',
        'sh_run_int_vlans.template',
        'sh_run_int_lag.template',
        'sh_run_int.template',
        'run_radius.template',
        'snmp_server_host.template',
    ],
    'ios' : [
        'sh_run_int.template',
        'sh_int_desc.template',
        'sh_cdp_ne_de.template',
        'sh_int_stats.template',
        'sh_ver.template',
        'sh_module.template',
        'sh_ver_chassis_switch.template',
        'sh_vlan.template',
        'run_radius.template',
        'sh_run_int_vlans.template',
        'sh_run_int_lag.template',
        'sh_run_ip_helper.template',
        'sh_run_dns.template',
        'snmp_server_host.template',
        'ntp_server_ip.template',
        'ip_dns_server_address.template',
        'sh_arp.template',
        'sh_mac_address.template',
        'sh_run_ip_helper.template'
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
                        'base_table_index' : os_templates['aos-s'].index('sh_run_vlans_id.template'),
                        'headers_to_include' : ['VLAN_ID', 'VLAN_NAME'],
                        'key' : 'VLAN_ID'
                    },
                    'parsed_info_to_add' : [
                        {
                            'table_name' : 'sh_vlans_ip',
                            'table_index' : os_templates['aos-s'].index('sh_run_vlans.template'),
                            'headers_to_add' : [
                                ('IP_ADDRESS', 'IP_ADDRESS'),
                                ('SUBNET', 'SUBNET')
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
                    'base_table_index' : os_templates['aos-s'].index('sh_system.template'),
                    'headers_to_include' : ['SERIAL_NUMBER','SYSTEM_NAME', 'SOFTWARE_VERSION'],
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
                'final_headers' : [
                    'LOCATION', 
                    'SUB_LOCATION', 
                    'SYSTEM_NAME', 
                    'MGMT_IP', 
                    'MGMT_SOURCE', 
                    'CHASSIS_MODEL', 
                    'SERIAL_NUMBER', 
                    'SOFTWARE_VERSION'
                    ],
                'convert_table' : True,
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
                            ('SYSTEM_DESCRIPTION', 'NEIGHBOR_DESCRIPTION'),
                            ('CHASSIS_ID', 'NEIGHBOR_IP')
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
                    },
                    {
                        'table_name' : 'sh_interfaces',
                        'table_index' : os_templates['aos-cx'].index('sh_interfaces.template'),
                        'headers_to_add' : [
                            ('TIME_UP', 'UP/DOWNTIME')
                        ]
                    }
                ],
                'final_headers' : [
                    'INTERFACE',
                    'NAME',
                    'NEIGHBOR_NAME',
                    'NEIGHBOR_DESCRIPTION',
                    'NEIGHBOR_IP',
                    'STATUS',
                    'UP/DOWNTIME',
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
                    'headers_to_include' : ['SERIAL_NUMBER','SYSTEM_NAME', 'SOFTWARE_VERSION'],
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
                'final_headers' : [
                    'LOCATION', 
                    'SUB_LOCATION', 
                    'SYSTEM_NAME', 
                    'MGMT_IP', 
                    'MGMT_SOURCE', 
                    'CHASSIS_MODEL', 
                    'SERIAL_NUMBER', 
                    'SOFTWARE_VERSION'],
                'convert_table' : True,
            }
        ],
    },
    'ios-xe' : {
        'device_port_table' :
        [
            {
                'table_name' : '',
                'base_table' : {
                    'base_table_index' : os_templates['ios-xe'].index('sh_int_desc.template'),
                    'headers_to_include' : ['INTERFACE', 'STATUS', 'PROTOCOL', 'DESCRIPTION'],
                    'key': 'INTERFACE'
                },
                'parsed_info_to_add': [
                    {
                        'table_name' : 'sh_int_stats',
                        'table_index' : os_templates['ios-xe'].index('sh_int_stats.template'),
                        'headers_to_add' : [
                            ('STATUS', 'CONNECTED'),
                            ('SPEED', 'SPEED'),
                            ('TYPE', 'TYPE')
                        ]
                    },
                    {
                        'table_name' : 'cdp_neighbors',
                        'table_index' : os_templates['ios-xe'].index('sh_cdp_ne_de.template'),
                        'headers_to_add' : [
                            ('DEVICE_ID', 'NEIGHBOR_NAME'),
                            ('PLATFORM', 'NEIGHBOR_DESCRIPTION'),
                            ('IP_ADDRESS', 'NEIGHBOR_IP')
                        ]
                    },
                    {
                        'table_name' : 'sh_run_int',
                        'table_index' : os_templates['ios-xe'].index('sh_run_int.template'),
                        'headers_to_add' : [
                            ('UNTAGGED_VLAN', 'NATIVE_VLAN'),
                            ('TAGGED_VLAN', 'TAGGED_VLAN'),
                        ]
                    },
                    {
                        'table_name' : 'sh_run_int_lag.template',
                        'table_index' : os_templates['ios-xe'].index('sh_run_int_lag.template'),
                        'headers_to_add' : [
                            ('LAG', 'LAG'),
                            ('CHANNEL_GROUP', 'CHANNEL_GROUP'),
                        ]
                    }
                ],
                'final_headers' : [
                    'INTERFACE',
                    'DESCRIPTION',
                    'NEIGHBOR_NAME',
                    'NEIGHBOR_DESCRIPTION',
                    'NEIGHBOR_IP',
                    'PROTOCOL',
                    'STATUS',
                    'CONNECTED',
                    'SPEED',
                    'TYPE',
                    'CHANNEL_GROUP',
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
                        'base_table_index' : os_templates['ios-xe'].index('sh_run_vlans.template'),
                        'headers_to_include' : ['VLAN_ID', 'VLAN_NAME'],
                        'key' : 'VLAN_ID'
                    },
                    'parsed_info_to_add' : [
                        {
                            'table_name' : 'sh_run_int_vlans',
                            'table_index' : os_templates['ios-xe'].index('sh_run_int_vlans.template'),
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
                    'base_table_index' : os_templates['ios-xe'].index('sh_module.template'),
                    'headers_to_include' : ['MODEL','SOFTWARE_VERSION', 'SERIAL_NUMBER'],
                    'key' : 'SERIAL_NUMBER'
                },
                'final_headers' : ['LOCATION', 'SUB_LOCATION', 'SYSTEM_NAME', 'MGMT_IP', 'MGMT_SOURCE', 'MODEL', 'SERIAL_NUMBER', 'SOFTWARE_VERSION'],
                'convert_table' : True,
                'matched_parameter_index' : 1
            }
        ],
    },
    'ios' : {
        'device_port_table' :
        [
            {
                'table_name' : '',
                'base_table' : {
                    'base_table_index' : os_templates['ios'].index('sh_int_desc.template'),
                    'headers_to_include' : ['INTERFACE', 'STATUS', 'PROTOCOL', 'DESCRIPTION'],
                    'key': 'INTERFACE'
                },
                'parsed_info_to_add': [
                    {
                        'table_name' : 'sh_int_stats',
                        'table_index' : os_templates['ios'].index('sh_int_stats.template'),
                        'headers_to_add' : [
                            ('STATUS', 'CONNECTED'),
                            ('SPEED', 'SPEED'),
                            ('TYPE', 'TYPE')
                        ]
                    },
                    {
                        'table_name' : 'cdp_neighbors',
                        'table_index' : os_templates['ios'].index('sh_cdp_ne_de.template'),
                        'headers_to_add' : [
                            ('DEVICE_ID', 'NEIGHBOR_NAME'),
                            ('PLATFORM', 'NEIGHBOR_DESCRIPTION'),
                            ('IP_ADDRESS', 'NEIGHBOR_IP')
                        ]
                    },
                    {
                        'table_name' : 'sh_run_int',
                        'table_index' : os_templates['ios'].index('sh_run_int.template'),
                        'headers_to_add' : [
                            ('UNTAGGED_VLAN', 'NATIVE_VLAN'),
                            ('TAGGED_VLAN', 'TAGGED_VLAN'),
                        ]
                    },
                    {
                        'table_name' : 'sh_run_int_lag.template',
                        'table_index' : os_templates['ios'].index('sh_run_int_lag.template'),
                        'headers_to_add' : [
                            ('LAG', 'LAG'),
                            ('CHANNEL_GROUP', 'CHANNEL_GROUP'),
                        ]
                    }
                ],
                'final_headers' : [
                    'INTERFACE',
                    'DESCRIPTION',
                    'NEIGHBOR_NAME',
                    'NEIGHBOR_DESCRIPTION',
                    'NEIGHBOR_IP',
                    'PROTOCOL',
                    'STATUS',
                    'CONNECTED',
                    'SPEED',
                    'TYPE',
                    'CHANNEL_GROUP',
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
                        'base_table_index' : os_templates['ios'].index('sh_vlan.template'),
                        'headers_to_include' : ['VLAN_ID', 'VLAN_NAME'],
                        'key' : 'VLAN_ID'
                    },
                    'parsed_info_to_add' : [
                        {
                            'table_name' : 'sh_run_int_vlans',
                            'table_index' : os_templates['ios'].index('sh_run_int_vlans.template'),
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
                    'base_table_index' : os_templates['ios'].index('sh_module.template'),
                    'headers_to_include' : ['SWITCH', 'PORTS', 'MODEL', 'SOFTWARE_VERSION'],
                    'key' : 'SWITCH'
                },
                'final_headers' : ['LOCATION', 'SUB_LOCATION', 'SYSTEM_NAME', 'MGMT_IP', 'MGMT_SOURCE', 'MODEL', 'MAC', 'SERIAL_NUMBER', 'SOFTWARE_VERSION'],
                'convert_table' : True,
            }
        ],
    },
    'nx-os' : {
        'device_port_table' :
        [
            {
                'table_name' : '',
                'base_table' : {
                    'base_table_index' : os_templates['nx-os'].index('sh_int_stats.template'),
                    'headers_to_include' : ['INTERFACE', 'DESCRIPTION', 'STATUS', 'SPEED', 'TYPE'],
                    'key': 'INTERFACE'
                },
                'parsed_info_to_add': [
                    {
                        'table_name' : 'cdp_neighbors',
                        'table_index' : os_templates['nx-os'].index('sh_cdp_ne_de.template'),
                        'headers_to_add' : [
                            ('DEVICE_ID', 'NEIGHBOR_NAME'),
                            ('PLATFORM', 'NEIGHBOR_DESCRIPTION'),
                            ('IP_ADDRESS', 'NEIGHBOR_IP')
                        ]
                    },
                    {
                        'table_name' : 'sh_run_int',
                        'table_index' : os_templates['nx-os'].index('sh_run_int.template'),
                        'headers_to_add' : [
                            ('UNTAGGED_VLAN', 'NATIVE_VLAN'),
                            ('TAGGED_VLAN', 'TAGGED_VLAN'),
                        ]
                    },
                    {
                        'table_name' : 'sh_run_int_lag.template',
                        'table_index' : os_templates['nx-os'].index('sh_run_int_lag.template'),
                        'headers_to_add' : [
                            ('LAG', 'LAG'),
                            ('CHANNEL_GROUP', 'CHANNEL_GROUP'),
                        ]
                    }
                ],
                'final_headers' : [
                    'INTERFACE',
                    'DESCRIPTION',
                    'NEIGHBOR_NAME',
                    'NEIGHBOR_DESCRIPTION',
                    'NEIGHBOR_IP',
                    'STATUS',
                    'SPEED',
                    'TYPE',
                    'CHANNEL_GROUP',
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
                        'base_table_index' : os_templates['nx-os'].index('sh_run_vlans.template'),
                        'headers_to_include' : ['VLAN_ID', 'VLAN_NAME'],
                        'key' : 'VLAN_ID'
                    },
                    'parsed_info_to_add' : [
                        {
                            'table_name' : 'sh_run_int_vlans',
                            'table_index' : os_templates['nx-os'].index('sh_run_int_vlans.template'),
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
                    'base_table_index' : os_templates['nx-os'].index('sh_module.template'),
                    'headers_to_include' : ['SWITCH','MODULE_TYPE','MODEL'],
                    'key' : 'SWITCH'
                },
                'parsed_info_to_add' : [
                    {
                        'table_name' : 'sh_module_mac_serial',
                        'table_index' : os_templates['nx-os'].index('sh_module_mac_serial.template'),
                        'headers_to_add' : [
                            ('MAC', 'MAC'),
                            ('SERIAL', 'SERIAL_NUMBER')
                        ]
                    }
                ],
                'final_headers' : [
                    'LOCATION', 
                    'SUB_LOCATION', 
                    'SWITCH',
                    'SYSTEM_NAME', 
                    'MGMT_IP', 
                    'MGMT_SOURCE', 
                    'MODULE_TYPE',
                    'MODEL', 
                    'SERIAL_NUMBER', 
                    'SOFTWARE_VERSION'
                    ],
                'convert_table' : True,
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
        'show interface',
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
    ],
    'ios-xe' : [
        'term len 0',
        'show access-list',
        'show call-home profile all',
        'show cdp neighbors',
        'show cdp neighbors detail',
        'show clock',
        'show env',
        'show env all',
        'show environment',
        'show environment all',
        'show etherchannel summary',
        'show feature | grep enabled',
        'show hsrp brief',
        'show interface description',
        'show interface status',
        'show interface status err-disabled',
        'show interface summary',
        'show interfaces',
        'show inventory',
        'show ip access-list',
        'show ip arp',
        'show ip bgp neighbors',
        'show ip bgp summary',
        'show ip dhcp binding',
        'show ip eigrp neighbor',
        'show ip interface brief',
        'show ip ospf neighbor',
        'show ip ospf database',
        'show ip protocols',
        'show ip route',
        'show ip route 0.0.0.0',
        'show ip route bgp',
        'show ip route eigrp',
        'show ip route ospf',
        'show ip route rip',
        'show ip route summary',
        'show ip ssh',
        'show ip traffic',
        'show license',
        'show license all',
        'show license host-id',
        'show license status',
        'show license summary',
        'show license udi',
        'show license usage',
        'show log',
        'show mac address-table dynamic',
        'show mac address-table',
        'show mac-address-table',
        'show mac-address-table dynamic',
        'show module',
        'show monitor',
        'show monitor detail',
        'show ntp status',
        'show ntp associations',
        'show port-channel summary',
        'show power in',
        'show redundancy',
        'show role',
        'show route-map',
        'show running',
        'show span',
        'show spanning-tree',
        'show spanning-tree blocked',
        'show spanning-tree summary',
        'show spanning-tree root',
        'show standby brief',
        'show stack-power',
        'show stack-power detail',
        'show stack-power budgeting',
        'show stack-power neighbors',
        'show stackwise-virtual',
        'show stackwise-virtual neighbors',
        'show stackwise-virtual link',
        'show stackwise-virtual dual-active-detection',
        'show switch',
        'show switch neighbors',
        'show switch stack-ports summary',
        'show switch stack-ring speed',
        'show switch detail',
        'show switch virtual dual-active fast-hello counters',
        'show switch virtual redundancy',
        'show switch virtual role detail',
        'show version',
        'show vlan',
        'show vlan brief',
        'show vtp',
        'show vtp status',
    ],
    'ios' : [
        'term len 0',
        'show access-list',
        'show call-home profile all',
        'show cdp neighbors',
        'show cdp neighbors detail',
        'show clock',
        'show env',
        'show env all',
        'show environment',
        'show environment all',
        'show etherchannel summary',
        'show feature | grep enabled',
        'show hsrp brief',
        'show interface description',
        'show interface status',
        'show interface status err-disabled',
        'show interface summary',
        'show interfaces',
        'show inventory',
        'show ip access-list',
        'show ip arp',
        'show ip bgp neighbors',
        'show ip bgp summary',
        'show ip dhcp binding',
        'show ip eigrp neighbor',
        'show ip interface brief',
        'show ip ospf neighbor',
        'show ip ospf database',
        'show ip protocols',
        'show ip route',
        'show ip route 0.0.0.0',
        'show ip route bgp',
        'show ip route eigrp',
        'show ip route ospf',
        'show ip route rip',
        'show ip route summary',
        'show ip ssh',
        'show ip traffic',
        'show license',
        'show license all',
        'show license host-id',
        'show license status',
        'show license summary',
        'show license udi',
        'show license usage',
        'show log',
        'show mac address-table dynamic',
        'show mac address-table',
        'show mac-address-table',
        'show mac-address-table dynamic',
        'show module',
        'show monitor',
        'show monitor detail',
        'show ntp status',
        'show ntp associations',
        'show port-channel summary',
        'show power in',
        'show redundancy',
        'show role',
        'show route-map',
        'show running',
        'show span',
        'show spanning-tree',
        'show spanning-tree blocked',
        'show spanning-tree summary',
        'show spanning-tree root',
        'show standby brief',
        'show stack-power',
        'show stack-power detail',
        'show stack-power budgeting',
        'show stack-power neighbors',
        'show stackwise-virtual',
        'show stackwise-virtual neighbors',
        'show stackwise-virtual link',
        'show stackwise-virtual dual-active-detection',
        'show switch',
        'show switch neighbors',
        'show switch stack-ports summary',
        'show switch stack-ring speed',
        'show switch detail',
        'show switch virtual dual-active fast-hello counters',
        'show switch virtual redundancy',
        'show switch virtual role detail',
        'show version',
        'show vlan',
        'show vlan brief',
        'show vtp',
        'show vtp status',
    ],
    'nx-os' : [
        'term len 0',
        'show access-list',
        'show call-home profile all',
        'show cdp neighbors',
        'show cdp neighbors detail',
        'show clock',
        'show env',
        'show env all',
        'show environment',
        'show environment all',
        'show etherchannel summary',
        'show feature | grep enabled',
        'show hsrp brief',
        'show interface description',
        'show interface status',
        'show interface status err-disabled',
        'show interface summary',
        'show interfaces',
        'show inventory',
        'show ip access-list',
        'show ip arp',
        'show ip bgp neighbors',
        'show ip bgp summary',
        'show ip dhcp binding',
        'show ip eigrp neighbor',
        'show ip interface brief',
        'show ip ospf neighbor',
        'show ip ospf database',
        'show ip protocols',
        'show ip route',
        'show ip route 0.0.0.0',
        'show ip route bgp',
        'show ip route eigrp',
        'show ip route ospf',
        'show ip route rip',
        'show ip route summary',
        'show ip ssh',
        'show ip traffic',
        'show license',
        'show license all',
        'show license host-id',
        'show license status',
        'show license summary',
        'show license udi',
        'show license usage',
        'show log',
        'show mac address-table dynamic',
        'show mac address-table',
        'show mac-address-table',
        'show mac-address-table dynamic',
        'show module',
        'show monitor',
        'show monitor detail',
        'show ntp status',
        'show ntp associations',
        'show port-channel summary',
        'show power in',
        'show redundancy',
        'show role',
        'show route-map',
        'show running',
        'show span',
        'show spanning-tree',
        'show spanning-tree blocked',
        'show spanning-tree summary',
        'show spanning-tree root',
        'show standby brief',
        'show stack-power',
        'show stack-power detail',
        'show stack-power budgeting',
        'show stack-power neighbors',
        'show stackwise-virtual',
        'show stackwise-virtual neighbors',
        'show stackwise-virtual link',
        'show stackwise-virtual dual-active-detection',
        'show switch',
        'show switch neighbors',
        'show switch stack-ports summary',
        'show switch stack-ring speed',
        'show switch detail',
        'show switch virtual dual-active fast-hello counters',
        'show switch virtual redundancy',
        'show switch virtual role detail',
        'show version',
        'show vlan',
        'show vlan brief',
        'show vtp',
        'show vtp status',
        'show vpc',
        'show vpc br',
        'show vpc consistency-parameters vlans',
        'show vpc orphan-ports',
        'show vpc statistics peer-link',
        'show vpc statistics peer-keepalive',
        'show vpc peer-keepalive',
        'show vpc role',

    ]
}