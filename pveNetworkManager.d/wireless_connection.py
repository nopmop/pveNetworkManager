#!/usr/bin/env python3

from config import RESERVED_IP, BRIDGE
from utils import run, run_wait, dhcp_change_iface

IPTABLES_RULES = {
	"nat": f"iptables -t nat -A POSTROUTING -s {RESERVED_IP} -o $interface -j MASQUERADE",
	"forward": f"iptables -A FORWARD -i {BRIDGE} -o $interface -j ACCEPT",
	"forward_related": f"iptables -A FORWARD -i $interface -o {BRIDGE} -m state --state RELATED,ESTABLISHED -j ACCEPT"
}

def iptables_modify(interface, state):
	for rule in ["nat", "forward", "forward_related"]:
		action = '-A' if state == 'up' else '-D'
		run(interface, state, IPTABLES_RULES[rule].replace('-A', action).replace("$interface", interface))

def bridge_address_modify(interface, state):
	if state == 'down':
		run(interface, state, f"ip addr del {RESERVED_IP} dev {BRIDGE}")
	elif state == 'up':
		run(interface, state, f"ip addr add {RESERVED_IP} dev {BRIDGE}")
					
def handle(interface, state):
	dhcp_change_iface(interface, state, BRIDGE, "/etc/default/isc-dhcp-server")
	iptables_modify(interface, state)
	bridge_address_modify(interface, state)
	if state == "up":
		if run_wait(interface, state, f"ip route show | grep default", interface):
			for line in (line for line in run(interface, state, f"ip route show default | grep -v {interface}").splitlines()):
				run(interface, state, f"ip route del default")
