import time
import subprocess
import re
import os

# cookie=0x6900000, duration=2626.495s, table=247, n_packets=0, n_bytes=0, priority=0 actions=drop
pat = '.*, (?P<tbl>table=[0-9]+), n_packets=(?P<packs>[0-9]+).*(?P<rule>priority.*)'


class flow:
	def __init__(self, match, line):
		self.key = match.group('tbl') + ',' + match.group('rule')
		self.count = int(match.group('packs'))
		self.line = line
		self.hits = 1

def parse(line):
	m = re.match(pat, line)
	if m is None: return None
	return flow(m, line)
		
def get():
	flow_out = subprocess.check_output('sudo ovs-ofctl -OOpenFlow13 dump-flows br-int'.split())
	ret = dict()
	for line in flow_out.split('\n'):
		f = parse(line)
		if f is None: continue
		ret[f.key] = f
	return ret

the_flows = get()
for i in range(1, 5):
	time.sleep(1.1)
	d = get()
	for k,v in d.iteritems():
		if k not in the_flows:
			the_flows[k] = v
			continue
		if v.count > the_flows[k].count:
			the_flows[k].hits += 1

for line in subprocess.check_output('sudo ovs-ofctl -OOpenFlow13 dump-flows br-int'.split()).split('\n'):
	f = parse(line)
	if f is None: continue
	if the_flows[f.key].hits > 4:
		print the_flows[f.key].line
		#os.system('sudo timeout 5 sudo ~/WIP/ovs-flow-snoop br-int "' + f.key + '"')
		#time.sleep(7)
