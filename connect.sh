sudo ovs-vsctl set-manager tcp:192.168.0.8:6640
sudo ovs-vsctl set-controller br-int tcp:192.168.0.8:6653
ssh 192.168.0.9 sudo ovs-vsctl set-manager tcp:192.168.0.8:6640
ssh 192.168.0.9 sudo ovs-vsctl set-controller br-int tcp:192.168.0.8:6653
