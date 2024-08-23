#!/usr/bin/env python3

from config import BRIDGE
from utils import run, run_wait
import re

def nexthop(interface, defaultroutes):
    matches = re.findall(r'\bvia\s+(\d{1,3}(?:\.\d{1,3}){3})\s+dev\s+(\S+)\b', defaultroutes)
    return {v: k for k, v in dict(matches).items()}.get(interface, None)

def get_ipv4(interface, state):
	return run(interface, state, f"ip addr show dev {interface} | grep inet | grep -v ':' | head -1 | awk '{{print $2}}'")

def handle(interface, state):
	if state == "down":
		bridge_ip = get_ipv4(BRIDGE, state)
		run(interface, state, f"ip route del default dev {BRIDGE}")
		run(interface, state, f"ip addr del {bridge_ip} dev {BRIDGE}")
		run(interface, state, f"brctl delif {BRIDGE} {interface}")
	if state == "up":
		if (defaultroutes := run_wait(interface, state, f"ip route show default", interface)):
			if(default_nexthop := nexthop(interface, defaultroutes)):
				default_ip = get_ipv4(interface, state)
				for line in (line for line in run(interface, state, f"ip route show default").splitlines()):
					run(interface, state, f"ip route del default")
				run(interface, state, f"ip addr del {default_ip} dev {interface}")
				run(interface, state, f"ip addr add {default_ip} dev {BRIDGE}")
				run(interface, state, f"brctl addif {BRIDGE} {interface}")
				run(interface, state, f"ip route add default via {default_nexthop} dev {BRIDGE}")