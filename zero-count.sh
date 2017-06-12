sudo ovs-ofctl -OOpenFlow13 dump-flows br-int | grep table=0 | wc -l
ssh 192.168.0.9 sudo ovs-ofctl -OOpenFlow13 dump-flows br-int | grep table=0 | wc -l

