set -x
ip=$1

port_uuid=$(neutron port-list | grep port-$ip | awk '{print $2}')
tap_name=$(echo $port_uuid | sed -e 's/\(...........\).*/tap\1/')

sudo ovs-vsctl del-port br-int $tap_name
neutron port-delete $port_uuid
