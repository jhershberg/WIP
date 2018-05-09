#set -x

NUM_BACK_COUNTS=5

function init_queue {
	echo $1 > .counts
	for i in $(seq 1 $NUM_BACK_COUNTS)
	do
		echo $1 >> .counts
	done
}

function enqueue_count {
	echo $1 >> .counts
	tail -$NUM_BACK_COUNTS .counts > .temp
	mv .temp .counts
	mv .flows.now .flows.last
}

function count_matches_in_queue {
	local ret=0
	for i in $(cat .counts)
	do
		if [ "$1" == "$i" ]
		then
			ret=$(expr $ret + 1)
		fi
	done
	echo $ret
}

if [ "$1" != once ]
then
	sudo ovs-ofctl -OOpenFlow13 dump-flows br-int | sed -e 's/.*duration=[^,]*,\ //' > .flows.last
	n=$(cat .flows.last | wc -l)
	init_queue $n
	touch .diff.last
	watch -d $0 once
	exit
fi

sleep 1
sudo ovs-ofctl -OOpenFlow13 dump-flows br-int | sed -e 's/.*duration=[^,]*,\ //' > .flows.now
diff -u .flows.last .flows.now | grep "^+" | grep -v flows.now > .diff.now
len=$(cat .diff.now | wc -l)

matches=$(count_matches_in_queue $len)
echo Line counts Prev $NUM_BACK_COUNTS:[$(cat .counts)] Current:[$len] $matches
if [ $matches -gt 1 ]
then
	echo Printing this round
	cat .diff.now
	mv .diff.now .diff.last
else
	echo Skipping this round
	cat .diff.last
fi

enqueue_count $len
