set -x
last_quad=$1
subnet_id=$(neutron subnet-list | awk '/S1/ {print $2}')
mac=$(uuidgen | md5sum | sed -e 's/\(..\)\(..\)\(..\)\(..\).*/52:54:\1:\2:\3:\4/')

neutron port-create --name josh${last_quad} --fixed-ip subnet_id=$(subnet_id),ip_address=192.168.2.10${last_quad} N1 --mac-address $mac --device-owner compute:nova --device-id $(uuidgen)

port_uuid=$(neutron port-list | grep $mac | awk '{print $2}')
tap_name=$(echo $port_uuid | sed -e 's/\(...........\).*/tap\1/')

sudo ovs-vsctl add-port br-int $tap_name -- set interface $tap_name type=internal -- set interface $tap_name external_ids=attached_mac=\"$mac\",iface-id=$port_uuid,iface-status=active
