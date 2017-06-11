action=c
num_nets=2
num_subnets=2
num_ports=2


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

			if [ $action = c ]
			then
				./mkport.sh $net_name $sub_name $ip || exit 1
			fi

			if [ $action = d ]
			then
				./delport.sh $ip
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
