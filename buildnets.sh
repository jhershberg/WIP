action=c
num_nets=10
num_subnets=5
num_ports=10

ovs_node_0=192.168.0.5
ovs_node_1=192.168.0.9
num_nodes=2

port_counter=0

# may need to adjust this
neutron quota-update --port 550

for net_num in $(seq 0 $(expr $num_nets - 1))
do
	net_name=net.${net_num}

	if [ $action = c ]
	then
		neutron net-create $net_name || exit 1
	fi

	for sub_num in $(seq 0 $(expr $num_subnets - 1))
	do
		sub_name=sub.${net_num}.${sub_num}
		pool_start=10.${net_num}.${sub_num}.100
		pool_end=10.${net_num}.${sub_num}.200
		cidr=10.${net_num}.${sub_num}.0/24

		if [ $action = c ]
		then
			neutron subnet-create ${net_name} --name ${sub_name} --allocation-pool start=${pool_start},end=${pool_end} $cidr || exit 1
		fi

		for port_num in $(seq 1 $num_ports)
		do
			ip=10.${net_num}.${sub_num}.$(expr 100 + $port_num)

			port_counter=$(expr $port_counter + 1)
			node=ovs_node_$(python -c "print $port_counter % $num_nodes")

			if [ $action = c ]
			then
				./mkport.sh $net_name $sub_name $ip ${!node} || exit 1
			fi

			if [ $action = d ]
			then
				./delport.sh $ip ${!node}
			fi
		done
		if [ $action = d ]
		then
			neutron subnet-delete $sub_name
		fi
	done
	if [ $action = d ]
	then
		neutron net-delete $net_name
	fi
done
