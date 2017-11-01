sudo ovs-ofctl -OOpenFlow13 dump-flows br-int > $1.flows.dump
sudo ovs-ofctl -OOpenFlow13 dump-groups br-int > $1.groups.dump
