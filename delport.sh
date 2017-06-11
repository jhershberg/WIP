set -x
ip=$1
node=$2

port_uuid=$(neutron port-list | grep port-$ip | awk '{print $2}')
tap_name=$(echo $port_uuid | sed -e 's/\(...........\).*/tap\1/')

if [ -z $node ]
then
	node sudo ovs-vsctl del-port br-int $tap_name
else
	ssh $node sudo ovs-vsctl del-port br-int $tap_name
fi

neutron port-delete $port_uuid
