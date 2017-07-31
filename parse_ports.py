#!/usr/bin/python 

import json
import sys
import re
from collections import OrderedDict

TABLE_NAMES = {0:'VLAN INTERFACE INGRESS',10:'VXLAN TRUNK INTERFACE',11:'TRUNK L2',12:'GRE TRUNK INTERFACE',17:'LPORT DISPATCHER',18:'DHCP EXTERNAL TUNNEL',19:'L3 GW MAC',20:'L3 LFIB',21:'L3 FIB',22:'L3 SUBNET ROUTE',23:'L3VNI EXTERNAL TUNNEL DEMUX',24:'L2VNI EXTERNAL TUNNEL DEMUX',25:'PDNAT',26:'PSNAT',27:'DNAT',28:'SNAT',36:'INTERNAL TUNNEL',38:'EXTERNAL TUNNEL',43:'ARP CHECK',44:'INBOUND NAPT',45:'IPV6',46:'OUTBOUND NAPT',47:'NAPT PFIB',48:'ELAN BASE',49:'ELAN SMAC LEARNED',50:'ELAN SMAC',51:'ELAN DMAC',52:'ELAN UNKNOWN DMAC',55:'ELAN FILTER EQUALS',60:'DHCP',70:'SCF UP SUB FILTER TCP BASED',72:'SCF DOWN SUB FILTER TCP BASED',75:'SCF CHAIN FWD',80:'L3 INTERFACE',81:'ARP RESPONDER',82:'SFC TRANSPORT CLASSIFIER',83:'SFC TRANSPORT INGRESS',84:'SFC TRANSPORT PATH MAPPER',85:'SFC TRANSPORT PATH MAPPER ACL',86:'SFC TRANSPORT NEXT HOP',87:'SFC TRANSPORT EGRESS',90:'QOS DSCP',100:'INGRESS SFC CLASSIFIER FILTER',101:'INGRESS SFC CLASSIFIER ACL',211:'INGRESS ACL',212:'INGRESS ACL REMOTE ACL',213:'INGRESS ACL FILTER',212:'INGRESS LEARN',213:'INGRESS LEARN ACL REMOTE ACL',214:'INGRESS LEARN ACL FILTER',219:'INGRESS COUNTERS',220:'EGRESS LPORT DISPATCHER',221:'EGRESS SFC CLASSIFIER FILTER',222:'EGRESS SFC CLASSIFIER NEXTHOP',223:'EGRESS SFC CLASSIFIER EGRESS',230:'EGRESS POLICY CLASSIFIER',231:'EGRESS POLICY ROUTING',241:'EGRESS ACL',242:'EGRESS ACL REMOTE ACL',243:'EGRESS ACL FILTER',242:'EGRESS LEARN',243:'EGRESS LEARN ACL REMOTE ACL',244:'EGRESS LEARN ACL FILTER',249:'EGRESS COUNTERS'}

bitmasks = { \
    0x0FFFFF0000000000: 'lport', \
    0x000000FFFF000000: 'service', \
    0xF000000000000000: 'service_idx', \
    0x0000000000FFFFFE: 'vrfid', \
    0x0000000000FFFFFE: 'remote_acl_id', \
    0x0000000000FFFFFE: 'policy_classifer_id', \
    0x08000000FFFFFF00: 'valid_tunnel_id_bit_and_tunnel_id', \
    0x40FFFFFF000000FF: 'label_itm', \
    0x00000000FFFFFF00: 'tunnel_id', \
    0x0000000000000001: 'sh', \
    0x000000FFFF000000: 'elan_subnet_route', \
    0x000000FFFFFFFFFE: 'subnet_route'}

OFCTL_SHOW = \
'''OFPT_FEATURES_REPLY (OF1.3) (xid=0x2): dpid:000078578233a2bd
n_tables:254, n_buffers:256
capabilities: FLOW_STATS TABLE_STATS PORT_STATS GROUP_STATS QUEUE_STATS
OFPST_PORT_DESC reply (OF1.3) (xid=0x3):
 1(tap3185d3dc-8d): addr:1f:50:00:00:00:00
     config:     PORT_DOWN
     state:      LINK_DOWN
     speed: 0 Mbps now, 0 Mbps max
 2(tunb22b564023b): addr:b6:1b:89:16:2b:a8
     config:     0
     state:      0
     speed: 0 Mbps now, 0 Mbps max
 3(tapf52a33b9-0a): addr:1e:a3:10:b5:b0:e4
     config:     PORT_DOWN
     state:      LINK_DOWN
     speed: 0 Mbps now, 0 Mbps max
 LOCAL(br-int): addr:78:57:82:33:a2:bd
     config:     PORT_DOWN
     state:      LINK_DOWN
     speed: 0 Mbps now, 0 Mbps max
OFPT_GET_CONFIG_REPLY (OF1.3) (xid=0x5): frags=normal miss_send_len=0
'''

PORTS_JSON = \
'''{ "ports": { "port": [ { "admin-state-up": true, "device-id": "e64a9a87-a267-48f4-ab8a-80dd4ddf9da0", "device-owner": "compute:nova", "fixed-ips": [ { "ip-address": "10.0.0.101", "subnet-id": "fca82111-2995-4b1e-9a64-ad7c229826af" } ], "mac-address": "52:54:e3:67:33:f8", "name": "port-10.0.0.101", "network-id": "95d621b1-3c7f-47f4-a36d-64be83577ee5", "neutron-binding:host-id": "", "neutron-binding:vif-type": "unbound", "neutron-binding:vnic-type": "normal", "neutron-portsecurity:port-security-enabled": true, "project-id": "622c78deacd246448d329dcbede2ffe0", "revision-number": 6, "security-groups": [ "3f2ec4f3-7eaf-4954-ad6b-2959855e308c" ], "status": "ACTIVE", "tenant-id": "622c78de-acd2-4644-8d32-9dcbede2ffe0", "uuid": "1fcf5c04-073e-450e-93d3-b9983b6dc37e" }, { "admin-state-up": true, "device-id": "dhcp27fd4e9e-b2ad-59c7-8b19-8a1d73b0e7da-95d621b1-3c7f-47f4-a36d-64be83577ee5", "device-owner": "network:dhcp", "fixed-ips": [ { "ip-address": "10.0.0.100", "subnet-id": "fca82111-2995-4b1e-9a64-ad7c229826af" } ], "mac-address": "fa:16:3e:4b:71:3d", "name": "", "network-id": "95d621b1-3c7f-47f4-a36d-64be83577ee5", "neutron-binding:host-id": "control", "neutron-binding:vif-details": [ { "details-key": "port_filter", "value": "true" } ], "neutron-binding:vif-type": "ovs", "neutron-binding:vnic-type": "normal", "neutron-portsecurity:port-security-enabled": false, "project-id": "622c78deacd246448d329dcbede2ffe0", "revision-number": 7, "status": "ACTIVE", "tenant-id": "622c78de-acd2-4644-8d32-9dcbede2ffe0", "uuid": "3185d3dc-8dab-4828-a3f9-b0de6fd24976" }, { "admin-state-up": true, "device-id": "4d383de7-5f9e-404a-a59f-58dd7dc20bb7", "device-owner": "compute:nova", "fixed-ips": [ { "ip-address": "10.0.0.102", "subnet-id": "fca82111-2995-4b1e-9a64-ad7c229826af" } ], "mac-address": "52:54:25:5e:21:d5", "name": "port-10.0.0.102", "network-id": "95d621b1-3c7f-47f4-a36d-64be83577ee5", "neutron-binding:host-id": "", "neutron-binding:vif-type": "unbound", "neutron-binding:vnic-type": "normal", "neutron-portsecurity:port-security-enabled": true, "project-id": "622c78deacd246448d329dcbede2ffe0", "revision-number": 6, "security-groups": [ "3f2ec4f3-7eaf-4954-ad6b-2959855e308c" ], "status": "ACTIVE", "tenant-id": "622c78de-acd2-4644-8d32-9dcbede2ffe0", "uuid": "f52a33b9-0a03-493f-95b2-0e6810adc83a" } ] } }'''

DUMP = \
'''OFPST_FLOW reply (OF1.3) (xid=0x2):
 cookie=0x8000001, duration=963.947s, table=0, n_packets=0, n_bytes=0, priority=5,in_port=2 actions=write_metadata:0x50000000001/0xfffff0000000001,goto_table:36
 cookie=0x8000000, duration=993.398s, table=0, n_packets=0, n_bytes=0, priority=4,in_port=3,vlan_tci=0x0000/0x1fff actions=write_metadata:0x20000000000/0xffffff0000000001,goto_table:17
 cookie=0x8000000, duration=993.398s, table=0, n_packets=0, n_bytes=0, priority=4,in_port=1,vlan_tci=0x0000/0x1fff actions=write_metadata:0x10000000000/0xffffff0000000001,goto_table:17
 cookie=0x8040000, duration=992.474s, table=17, n_packets=0, n_bytes=0, priority=10,metadata=0x10000000000/0xffffff0000000000 actions=load:0x1->NXM_NX_REG1[0..19],load:0x1388->NXM_NX_REG7[0..15],write_metadata:0xa000011388000000/0xfffffffffffffffe,goto_table:48
 cookie=0x8040000, duration=992.470s, table=17, n_packets=0, n_bytes=0, priority=10,metadata=0x9000020000000000/0xffffff0000000000 actions=load:0x2->NXM_NX_REG1[0..19],load:0x1388->NXM_NX_REG7[0..15],write_metadata:0xa000021388000000/0xfffffffffffffffe,goto_table:48
 cookie=0x6900000, duration=992.470s, table=17, n_packets=0, n_bytes=0, priority=10,metadata=0x20000000000/0xffffff0000000000 actions=write_metadata:0x9000021388000000/0xfffffffffffffffe,goto_table:211
 cookie=0x8000000, duration=993.398s, table=17, n_packets=0, n_bytes=0, priority=0,metadata=0x8000000000000000/0xf000000000000000 actions=write_metadata:0x9000000000000000/0xf000000000000000,goto_table:80
 cookie=0x6800000, duration=993.398s, table=18, n_packets=0, n_bytes=0, priority=0 actions=goto_table:38
 cookie=0x1080000, duration=993.204s, table=19, n_packets=0, n_bytes=0, priority=100,arp,arp_op=2 actions=CONTROLLER:65535,resubmit(,17)
 cookie=0x1080000, duration=993.204s, table=19, n_packets=0, n_bytes=0, priority=100,arp,arp_op=1 actions=group:5002
 cookie=0x1080000, duration=993.204s, table=19, n_packets=0, n_bytes=0, priority=0 actions=resubmit(,17)
 cookie=0x1030000, duration=993.204s, table=20, n_packets=0, n_bytes=0, priority=0 actions=goto_table:80
 cookie=0x8000004, duration=993.204s, table=22, n_packets=0, n_bytes=0, priority=0 actions=CONTROLLER:65535
 cookie=0x1080000, duration=993.204s, table=23, n_packets=0, n_bytes=0, priority=0 actions=resubmit(,17)
 cookie=0x9001388, duration=992.484s, table=36, n_packets=0, n_bytes=0, priority=5,tun_id=0x3b actions=write_metadata:0x1388000000/0xfffffffff000000,goto_table:51
 cookie=0x9051388, duration=993.398s, table=38, n_packets=0, n_bytes=0, priority=5,tun_id=0x3b actions=write_metadata:0x1388000000/0xfffffffff000000,goto_table:51
 cookie=0x4000000, duration=993.398s, table=45, n_packets=0, n_bytes=0, priority=0 actions=resubmit(,17)
 cookie=0x8500000, duration=993.398s, table=48, n_packets=0, n_bytes=0, priority=0 actions=resubmit(,49),resubmit(,50)
 cookie=0x8051388, duration=992.484s, table=50, n_packets=0, n_bytes=0, priority=20,metadata=0x11388000000/0xfffffffff000000,dl_src=fa:16:3e:4b:71:3d actions=goto_table:51
 cookie=0x8051388, duration=992.479s, table=50, n_packets=0, n_bytes=0, priority=20,metadata=0x21388000000/0xfffffffff000000,dl_src=52:54:25:5e:21:d5 actions=goto_table:51
 cookie=0x8050001, duration=993.204s, table=50, n_packets=0, n_bytes=0, priority=10,reg4=0x1 actions=goto_table:51
 cookie=0x8050000, duration=993.398s, table=50, n_packets=0, n_bytes=0, priority=0 actions=CONTROLLER:65535,learn(table=49,hard_timeout=10,priority=0,cookie=0x8600000,NXM_OF_ETH_SRC[],NXM_NX_REG1[0..19],load:0x1->NXM_NX_REG4[0..7]),goto_table:51
 cookie=0x8031388, duration=992.485s, table=51, n_packets=0, n_bytes=0, priority=20,metadata=0x1388000000/0xffff000000,dl_dst=fa:16:3e:4b:71:3d actions=load:0x100->NXM_NX_REG6[],resubmit(,220)
 cookie=0x8031388, duration=992.479s, table=51, n_packets=0, n_bytes=0, priority=20,metadata=0x1388000000/0xffff000000,dl_dst=52:54:25:5e:21:d5 actions=load:0x200->NXM_NX_REG6[],resubmit(,220)
 cookie=0x8031388, duration=964.514s, table=51, n_packets=0, n_bytes=0, priority=20,metadata=0x1388000000/0xffff000000,dl_dst=52:54:e3:67:33:f8 actions=drop
 cookie=0x8030000, duration=993.204s, table=51, n_packets=0, n_bytes=0, priority=15,dl_dst=01:80:c2:00:00:00/ff:ff:ff:ff:ff:f0 actions=drop
 cookie=0x8030000, duration=993.204s, table=51, n_packets=0, n_bytes=0, priority=0 actions=goto_table:52
 cookie=0x8701388, duration=992.484s, table=52, n_packets=0, n_bytes=0, priority=5,metadata=0x1388000000/0xffff000001 actions=write_actions(group:210000)
 cookie=0x8701388, duration=992.484s, table=52, n_packets=0, n_bytes=0, priority=5,metadata=0x1388000001/0xffff000001 actions=write_actions(group:209999)
 cookie=0x8800001, duration=992.484s, table=55, n_packets=0, n_bytes=0, priority=10,tun_id=0x1,metadata=0x10000000000/0xfffff0000000000 actions=drop
 cookie=0x8800002, duration=992.479s, table=55, n_packets=0, n_bytes=0, priority=10,tun_id=0x2,metadata=0x20000000000/0xfffff0000000000 actions=drop
 cookie=0x8800001, duration=992.484s, table=55, n_packets=0, n_bytes=0, priority=9,tun_id=0x1 actions=load:0x100->NXM_NX_REG6[],resubmit(,220)
 cookie=0x8800002, duration=992.479s, table=55, n_packets=0, n_bytes=0, priority=9,tun_id=0x2 actions=load:0x200->NXM_NX_REG6[],resubmit(,220)
 cookie=0x6800000, duration=993.398s, table=60, n_packets=0, n_bytes=0, priority=0 actions=resubmit(,17)
 cookie=0x1030000, duration=993.204s, table=80, n_packets=0, n_bytes=0, priority=0 actions=resubmit(,17)
 cookie=0x8220000, duration=993.204s, table=81, n_packets=0, n_bytes=0, priority=0 actions=drop
 cookie=0x4000001, duration=993.398s, table=90, n_packets=0, n_bytes=0, priority=0 actions=resubmit(,17)
 cookie=0x6900000, duration=993.082s, table=211, n_packets=0, n_bytes=0, priority=63010,udp,metadata=0x20000000000/0xfffff0000000000,tp_src=68,tp_dst=67 actions=resubmit(,17)
 cookie=0x6900000, duration=993.077s, table=211, n_packets=0, n_bytes=0, priority=63010,udp6,metadata=0x20000000000/0xfffff0000000000,tp_src=546,tp_dst=547 actions=resubmit(,17)
 cookie=0x6900000, duration=993.071s, table=211, n_packets=0, n_bytes=0, priority=63010,udp,metadata=0x20000000000/0xfffff0000000000,tp_src=67,tp_dst=68 actions=drop
 cookie=0x6900000, duration=993.065s, table=211, n_packets=0, n_bytes=0, priority=63010,udp6,metadata=0x20000000000/0xfffff0000000000,tp_src=547,tp_dst=546 actions=drop
 cookie=0x6900000, duration=993.058s, table=211, n_packets=0, n_bytes=0, priority=63020,icmp6,metadata=0x20000000000/0xfffff0000000000,icmp_type=134,icmp_code=0 actions=drop
 cookie=0x6900000, duration=993.008s, table=211, n_packets=0, n_bytes=0, priority=63010,icmp6,metadata=0x20000000000/0xfffff0000000000,icmp_type=133,icmp_code=0 actions=resubmit(,17)
 cookie=0x6900000, duration=993.008s, table=211, n_packets=0, n_bytes=0, priority=63010,icmp6,metadata=0x20000000000/0xfffff0000000000,icmp_type=135,icmp_code=0 actions=resubmit(,17)
 cookie=0x6900000, duration=993.008s, table=211, n_packets=0, n_bytes=0, priority=63010,icmp6,metadata=0x20000000000/0xfffff0000000000,icmp_type=136,icmp_code=0 actions=resubmit(,17)
 cookie=0x6900000, duration=993.008s, table=211, n_packets=0, n_bytes=0, priority=63010,arp,metadata=0x20000000000/0xfffff0000000000,arp_sha=52:54:25:5e:21:d5 actions=resubmit(,17)
 cookie=0x6900000, duration=993.006s, table=211, n_packets=0, n_bytes=0, priority=61010,ip,dl_src=52:54:25:5e:21:d5,nw_src=10.0.0.102 actions=ct(table=212,zone=5000)
 cookie=0x6900000, duration=993.006s, table=211, n_packets=0, n_bytes=0, priority=61010,ipv6,dl_src=52:54:25:5e:21:d5,ipv6_src=fe80::5054:25ff:fe5e:21d5 actions=ct(table=212,zone=5000)
 cookie=0x6900000, duration=993.398s, table=211, n_packets=0, n_bytes=0, priority=0 actions=drop
 cookie=0x6900000, duration=992.966s, table=212, n_packets=0, n_bytes=0, priority=50,ip,metadata=0x1388000000/0xffff000000,nw_dst=10.0.0.102 actions=write_metadata:0x2/0xfffffe,goto_table:213
 cookie=0x6900000, duration=965.222s, table=212, n_packets=0, n_bytes=0, priority=50,ip,metadata=0x1388000000/0xffff000000,nw_dst=10.0.0.101 actions=write_metadata:0x2/0xfffffe,goto_table:213
 cookie=0x6900000, duration=992.958s, table=212, n_packets=0, n_bytes=0, priority=50,ipv6,metadata=0x1388000000/0xffff000000,ipv6_dst=fe80::5054:25ff:fe5e:21d5 actions=write_metadata:0x2/0xfffffe,goto_table:213
 cookie=0x6900000, duration=965.211s, table=212, n_packets=0, n_bytes=0, priority=50,ipv6,metadata=0x1388000000/0xffff000000,ipv6_dst=fe80::5054:e3ff:fe67:33f8 actions=write_metadata:0x2/0xfffffe,goto_table:213
 cookie=0x6900000, duration=993.398s, table=212, n_packets=0, n_bytes=0, priority=0 actions=goto_table:213
 cookie=0x6900000, duration=993.204s, table=213, n_packets=0, n_bytes=0, priority=62020,ct_state=-new+est-rel-inv+trk actions=resubmit(,17)
 cookie=0x6900000, duration=993.204s, table=213, n_packets=0, n_bytes=0, priority=62020,ct_state=-new-est+rel-inv+trk actions=resubmit(,17)
 cookie=0x6900001, duration=992.992s, table=213, n_packets=0, n_bytes=0, priority=62015,ct_state=+inv+trk,metadata=0x20000000000/0xfffff0000000000 actions=drop
 cookie=0x6900000, duration=992.979s, table=213, n_packets=0, n_bytes=0, priority=61010,ct_state=+new+trk,ip,metadata=0x20000000000/0xfffff0000000000 actions=ct(commit,zone=5000),resubmit(,17)
 cookie=0x6900000, duration=992.973s, table=213, n_packets=0, n_bytes=0, priority=61010,ct_state=+new+trk,ipv6,metadata=0x20000000000/0xfffff0000000000 actions=ct(commit,zone=5000),resubmit(,17)
 cookie=0x6900001, duration=993.003s, table=213, n_packets=0, n_bytes=0, priority=50,ct_state=+new+trk,metadata=0x20000000000/0xfffff0000000000 actions=drop
 cookie=0x6900000, duration=993.398s, table=213, n_packets=0, n_bytes=0, priority=0 actions=drop
 cookie=0x8000007, duration=993.014s, table=220, n_packets=0, n_bytes=0, priority=9,reg6=0x100 actions=output:1
 cookie=0x6900000, duration=993.012s, table=220, n_packets=0, n_bytes=0, priority=6,reg6=0x200 actions=load:0x90000200->NXM_NX_REG6[],write_metadata:0x1388000000/0xfffffffffe,goto_table:241
 cookie=0x8000007, duration=993.012s, table=220, n_packets=0, n_bytes=0, priority=9,reg6=0x90000200 actions=output:3
 cookie=0x8000007, duration=963.953s, table=220, n_packets=0, n_bytes=0, priority=9,reg6=0x500 actions=output:2
 cookie=0x8000230, duration=993.398s, table=230, n_packets=0, n_bytes=0, priority=0 actions=resubmit(,220)
 cookie=0x8000231, duration=993.398s, table=231, n_packets=0, n_bytes=0, priority=0 actions=resubmit(,220)
 cookie=0x6900000, duration=993.204s, table=241, n_packets=0, n_bytes=0, priority=63010,udp,reg6=0x200/0xfffff00,tp_src=67,tp_dst=68 actions=resubmit(,220)
 cookie=0x6900000, duration=993.204s, table=241, n_packets=0, n_bytes=0, priority=63010,udp6,reg6=0x200/0xfffff00,tp_src=547,tp_dst=546 actions=resubmit(,220)
 cookie=0x6900000, duration=993.204s, table=241, n_packets=0, n_bytes=0, priority=63010,icmp6,reg6=0x200/0xfffff00,icmp_type=130,icmp_code=0 actions=resubmit(,220)
 cookie=0x6900000, duration=993.204s, table=241, n_packets=0, n_bytes=0, priority=63010,icmp6,reg6=0x200/0xfffff00,icmp_type=135,icmp_code=0 actions=resubmit(,220)
 cookie=0x6900000, duration=993.197s, table=241, n_packets=0, n_bytes=0, priority=63010,icmp6,reg6=0x200/0xfffff00,icmp_type=136,icmp_code=0 actions=resubmit(,220)
 cookie=0x6900000, duration=993.187s, table=241, n_packets=0, n_bytes=0, priority=63010,arp,reg6=0x200/0xfffff00 actions=resubmit(,220)
 cookie=0x6900000, duration=993.146s, table=241, n_packets=0, n_bytes=0, priority=61010,ip,dl_dst=52:54:25:5e:21:d5,nw_dst=10.0.0.102 actions=ct(table=242,zone=5000)
 cookie=0x6900000, duration=993.133s, table=241, n_packets=0, n_bytes=0, priority=61010,ipv6,dl_dst=52:54:25:5e:21:d5,ipv6_dst=fe80::5054:25ff:fe5e:21d5 actions=ct(table=242,zone=5000)
 cookie=0x6900000, duration=993.398s, table=241, n_packets=0, n_bytes=0, priority=0 actions=drop
 cookie=0x6900000, duration=993.094s, table=242, n_packets=0, n_bytes=0, priority=50,ip,metadata=0x1388000000/0xffff000000,nw_src=10.0.0.102 actions=write_metadata:0x2/0xfffffe,goto_table:243
 cookie=0x6900000, duration=965.349s, table=242, n_packets=0, n_bytes=0, priority=50,ip,metadata=0x1388000000/0xffff000000,nw_src=10.0.0.101 actions=write_metadata:0x2/0xfffffe,goto_table:243
 cookie=0x6900000, duration=993.088s, table=242, n_packets=0, n_bytes=0, priority=50,ipv6,metadata=0x1388000000/0xffff000000,ipv6_src=fe80::5054:25ff:fe5e:21d5 actions=write_metadata:0x2/0xfffffe,goto_table:243
 cookie=0x6900000, duration=965.334s, table=242, n_packets=0, n_bytes=0, priority=50,ipv6,metadata=0x1388000000/0xffff000000,ipv6_src=fe80::5054:e3ff:fe67:33f8 actions=write_metadata:0x2/0xfffffe,goto_table:243
 cookie=0x6900000, duration=993.398s, table=242, n_packets=0, n_bytes=0, priority=0 actions=goto_table:243
 cookie=0x6900000, duration=993.204s, table=243, n_packets=0, n_bytes=0, priority=62020,ct_state=-new+est-rel-inv+trk actions=resubmit(,220)
 cookie=0x6900000, duration=993.204s, table=243, n_packets=0, n_bytes=0, priority=62020,ct_state=-new-est+rel-inv+trk actions=resubmit(,220)
 cookie=0x6900001, duration=993.118s, table=243, n_packets=0, n_bytes=0, priority=62015,ct_state=+inv+trk,reg6=0x200/0xfffff00 actions=drop
 cookie=0x6900000, duration=993.110s, table=243, n_packets=0, n_bytes=0, priority=61010,ct_state=+new+trk,ipv6,reg6=0x200/0xfffff00,metadata=0x2/0xfffffe actions=ct(commit,zone=5000),resubmit(,220)
 cookie=0x6900000, duration=993.100s, table=243, n_packets=0, n_bytes=0, priority=61010,ct_state=+new+trk,ip,reg6=0x200/0xfffff00,metadata=0x2/0xfffffe actions=ct(commit,zone=5000),resubmit(,220)
 cookie=0x6900001, duration=993.125s, table=243, n_packets=0, n_bytes=0, priority=50,ct_state=+new+trk,reg6=0x200/0xfffff00 actions=drop
 cookie=0x6900000, duration=993.398s, table=243, n_packets=0, n_bytes=0, priority=0 actions=drop'''

PORT_PATTERN=' (?P<port_num>[0-9]*)\((?P<port_name>.*)\): addr:.*'

port_lookup = {}

def get_bitmask_fields(bitmask, value):
    res = []
    for (mask, name) in bitmasks.iteritems():
        if mask == (mask & bitmask):
            res.append('%s=%0x' % (name, mask & int(value, 16)))
    return ','.join(res)
    
def parse_actions(actions, res):

    action = ''
    in_parens = 0
    for c in actions:
        if in_parens:
            if c == ')':
                in_parens = 0
            action += c
        else:
            if c == ',':
                res.actions.append(note_taker.add_action_note(action))
                action = ''
                continue

            if c == '(':
                in_parens = 1
            action += c
    if len(action):
        res.actions.append(note_taker.add_action_note(action))
    return res

class Flow:
    def __init__(self):
        self.attrs = OrderedDict()
        self.matches = OrderedDict()
        self.actions = []
    def __str__(self):
        return 'Attrs: ' + str(self.attrs) + \
            '\nMatches: ' + str(self.matches) + \
            '\nActions: ' + str(self.actions)

    def format(self):
        res = ''
        for (k,v) in self.matches.iteritems():
            if v:
                res += k + '=' + v
            else:
                res += k
            res +=  ', '
        if self.matches:
            res = res[0:-2] + ' '
        res += 'actions='
        for i in self.actions:
            res += i + ', '
        return res

def is_meta(k):
    return k in ['n_packets', 'n_bytes', 'priority', 'cookie', 'duration', 'table']

class NoteTaker:
    def __init__(self):
        pass

    def add_action_note(self, action):
        fields = action.split(':')
        if len(fields) != 2:
            return action
        return fields[0] + ':' + self.add_note(fields[0], fields[1])
    def add_note(self, key, val):
        func = getattr(self, key, None)
        if not func:
            return val
        return func(val)

    def _note(self, val, note):
        return val + ' (%s)' % note

    def nw_src(self, val):
        if val not in port_lookup:
            return val
        return self._note(val, port_lookup[val]['mac'])

    def nw_dst(self, val):
        if val not in port_lookup:
            return val
        return self._note(val, port_lookup[val]['mac'])

    def dl_dst(self, val):
        if val not in port_lookup:
            return val
        return self._note(val, port_lookup[val]['ip'])

    def dl_src(self, val):
        if val not in port_lookup:
            return val
        return self._note(val, port_lookup[val]['ip'])

    def in_port(self, val):
        if val not in port_lookup:
            return val
        return self._note(val, port_lookup[val]['ip'] + ',' + port_lookup[val]['name'])

    def write_metadata(self, val):
        return self.metadata(val)

    def metadata(self, val):
        (value, mask) = val.split('/')
        mask = int(mask, 16)
        return self._note(val, str(get_bitmask_fields(mask, value)))


note_taker = NoteTaker()

def parse_flow(flow):
    split_res = flow.split(' actions=')
    if len(split_res) != 2: 
        print 'ERROR parsing %s' % flow
        return
    (raw_attrs, raw_actions) = split_res

    res = Flow()
    for kv in [s.strip() for s in raw_attrs.split(',')]:
        kv_split = kv.split('=')
        if len(kv_split) == 1:
            res.matches[kv] = ''
        elif len(kv_split) == 2:
            if is_meta(kv_split[0]):
                res.attrs[kv_split[0]] = kv_split[1]
            else:
                res.matches[kv_split[0]] = note_taker.add_note(kv_split[0], kv_split[1])

    parse_actions(raw_actions, res)
    return res

def parse_flows():
    flows = []
    for line in DUMP.split('\n'):
        f = parse_flow(line)
        if f: flows.append(f)

    tbl = None
    for flow in flows:
        t = flow.attrs['table']
        if t != tbl:
            tbl = t
            print 'TABLE=' + tbl
        print ' ' + flow.format()

def extract_ports(ofctl_show):
    res = {}
    for line in ofctl_show.split('\n'):
        match = re.match(PORT_PATTERN, line)
        if not match:
            continue
        num = match.group('port_num')
        name = match.group('port_name')
        res[name[3:]] = (num, name)
    return res

def jpath(root, path, val_on_not_found=None):
    ptr = root
    for key in path.split('/'):
        if key not in ptr:
            return val_on_not_found
        ptr = ptr[key]
    return ptr

def jpath_in_list(list, path, val_on_not_found=None):
    for root in list:
        res = jpath(root, path, val_on_not_found)
        if res != val_on_not_found:
            return res
    return val_on_not_found

def parse_ports_json(text):
    jzon = json.loads(text)
    res = []
    for port in jpath(jzon, 'ports/port', []):
        ip = jpath_in_list(jpath(port, 'fixed-ips', []), 'ip-address', None)
        mac = jpath(port, 'mac-address', None)
        uuid = jpath(port, 'uuid', None)
        fields = {'ip': ip, 'mac': mac, 'uuid': uuid}
        add_of_port_fields(fields)
        for k in fields.itervalues():
            port_lookup[k] = fields
        res.append(fields)
    #add none neutron ports
    #for (name, num) in of_ports.iteritems():
    #    print num
    #    if num not in port_lookup:
    #        port_lookup[num] = {'name': name, 'num': num}


of_ports = None
def add_of_port_fields(port_dict):
    global of_ports
    if not of_ports:
        of_ports = extract_ports(OFCTL_SHOW)
    key = port_dict['uuid'][0:11]
    if key in of_ports:
        (num, name) = of_ports[key]
        port_dict['num'] = num
        port_dict['name'] = name
parse_ports_json(PORTS_JSON)
parse_flows()
