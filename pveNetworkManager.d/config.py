# Configuration:
SYSLOG_NAME = "pveNetworkManager" # name for syslog
BRIDGE = "vmbr0" # bridged (not NAT) bridge in Proxmox
ETHERNET = "enp44s0" # ethernet
WIRELESS = "wlo1" # wireless
RESERVED_IP = "10.20.20.1/24" # ip used by BRIDGE when switching from bridged mode to NAT mode
DEBUG = False # activates snapshotting (before & after each command) of routes, iptables, and brctl in syslog
TIMEOUT = 5 # time to wait for a DHCP reply (since the moment in which NetworkManager brings the interface "up")