# pveNetworkManager

## Overview

Proxmox uses `/etc/network/interfaces` to manage network interfaces. This conflicts with NetworkManager, which typically controls network interfaces through its own configuration files.

Previously, a common workaround to use NetworkManager with Proxmox involved setting `managed=false` in `/etc/NetworkManager/NetworkManager.conf` causing NetworkManager to ignore Proxmox interfaces, and thus causing some applications (that rely on NetworkManager notifications of connectivity-changes, such as `Discover`, the package manager) to believe that the network is unavailable. 

**pveNetworkManager** solves this by dynamically configuring components in Proxmox when the state of the interfaces changes, in a way that avoids conflicts. 

## Features

- Small and fast, ~150 lines, written in Python (and 2 lines of BASH).
- No need to shut down running VMs: 
    - When Ethernet is active, the interface is automatically joined to the bridge (e.g. `vmbr0`) to provide connectivity seamlessly.
    - When Wireless is active, the bridge (e.g. `vmbr0`) automatically switches to NAT mode (since Wireless can't be bridged) and runs a DHCP server, so that running VMs can simply request an IP and keep working.

## Caveats

- Only 1 physical interface (Ethernet or Wireless, configured via DHCP or not) must be active at any given time, and it must provide a default gateway.

## Prerequisites

1. **Dependencies**:

    You have `isc-dhcp-server` installed.

    ```bash
    sudo apt-get install isc-dhcp-server
    ```

2. **NetworkManager settings**:

    You have the following in `/etc/NetworkManager/NetworkManager.conf`:

    ```ini
    [ifupdown]
    managed=true
    ```

3. **Proxmox Network Configuration**:

    - You have at least ONE bridged (not NAT) bridge in Proxmox (i.e.: `vmbr0`).
    - You have `dummy` in `/etc/modules` (if not, run: `echo dummy | sudo tee -a /etc/modules`).
    - You have a dummy interface (which does nothing) assigned to the bridged bridge (i.e.: `vmbr0`).
    - You have no physical interfaces in `/etc/network/interfaces`.
    
    ```ini
    auto lo
    iface lo inet loopback

    audo dummy0
    iface dummy0 inet manual
        post-up ip link add dummy0 type dummy

    auto vmbr0
    iface vmbr0 inet manual
            bridge-ports 
            bridge-stp off
            bridge-fd 0

    source /etc/network/interfaces.d/*
    ```
    Note 1: if you have any other interfaces (like a NAT bridge, etc.) the software should run fine, but you run it AT YOUR OWN RISK. 
    Note 2: Make sure the configurations of [iptables, routes] are backed up.

## Installation

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/yourusername/pveNetworkManager.git
    cd pveNetworkManager
    ```
2. **Configure `isc-dhcp-server`**:

    Reserve a subnet in `/etc/dhcp/dhcpd.conf` which will be attached to `vmbr0` when it's required to switch to NAT mode.
    For example, I'm reserving `10.20.20.0/24` whose first IP `10.20.20.1` I will add to `pveNetworkManager.d/config.py`

    ```ini
        subnet 10.20.20.0 netmask 255.255.255.0 {
            range 10.20.20.2 10.20.20.254;
            option routers 10.20.20.1;
            option domain-name-servers 8.8.8.8;
        }
    ```

2. **Configure `pveNetworkManager.d/config.py`**:

    Change the parameters below, changing at least the RESERVED_IP according to `/etc/dhcp/dhcpd.conf`
    
    ```python
        SYSLOG_NAME = "pveNetworkManager" # name for syslog
        BRIDGE = "vmbr0" # bridged (not NAT) bridge in Proxmox
        ETHERNET = "enp44s0" # ethernet
        WIRELESS = "wlo1" # wireless
        RESERVED_IP = "10.20.20.1/24" # ip used by BRIDGE when switching from bridged mode to NAT mode
        DEBUG = False # activates snapshotting (before & after each command) of routes, iptables, and brctl in syslog
        TIMEOUT = 5 # time to wait for a DHCP reply (since the moment in which NetworkManager brings the interface "up")
    ```
3. **Install**:
    
    As root type: 
    ```
    make check
    make install
    ```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or issues, please use the appropriate Github section.

