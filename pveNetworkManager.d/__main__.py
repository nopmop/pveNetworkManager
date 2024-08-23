from wired_connection import handle as handle_wired
from wireless_connection import handle as handle_wireless
from config import ETHERNET, WIRELESS

def main(interface, state):
	if state == "up" or state == "down":
		if interface == ETHERNET:
			handle_wired(interface, state)
		elif interface == WIRELESS:
			handle_wireless(interface, state)

if __name__ == "__main__":
	import sys
	if len(sys.argv) != 3:
		print("Usage: script.py <interface> <state>")
		sys.exit(1)
	interface = sys.argv[1]
	state = sys.argv[2]
	main(interface, state)
