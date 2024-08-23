# Makefile for pveNetworkManager installation

# Define variables
SRC_FILE = 99-pveNetworkManager
SRC_DIR = pveNetworkManager.d
DEST_DIR = /etc/NetworkManager/dispatcher.d/
PERMISSIONS = sudo chown -R root:root $(DEST_DIR)

# Prerequisites to be checked
CMD_IP = /sbin/ip
CMD_IPTABLES = /usr/sbin/iptables
CMD_BRCTL = /usr/sbin/brctl
CMD_SERVICE = /usr/sbin/service
CMD_GREP = /usr/bin/grep
HEAD = /usr/bin/head
AWK = /usr/bin/awk
DHCP_DEFAULTS_FILE = /etc/default/isc-dhcp-server
DHCP_SERVICE = isc-dhcp-server

check:
	@for cmd in $(CMD_IP) $(CMD_IPTABLES) $(CMD_BRCTL) $(CMD_SERVICE) $(CMD_GREP) $(HEAD) $(AWK); do \
		if [ ! -f $$cmd ]; then \
			echo "File not found: $$cmd"; \
			exit 1; \
		fi \
	done

	@if [ ! -f $(DHCP_DEFAULTS_FILE) ]; then \
		echo "File not found: $(DHCP_DEFAULTS_FILE)"; \
		exit 1; \
	fi

	@if systemctl is-active --quiet $(DHCP_SERVICE); then \
		true; \
	else \
		echo "Service not active: $(DHCP_SERVICE)"; \
		exit 1; \
	fi

	@echo "All checks passed."

install:
	@echo "Copying $(SRC_FILE) to $(DEST_DIR)..."
	sudo cp $(SRC_FILE) $(DEST_DIR)
	@echo "Copying $(SRC_DIR) to $(DEST_DIR)..."
	sudo cp -r $(SRC_DIR) $(DEST_DIR)
	@echo "Setting ownership of $(DEST_DIR) to root:root..."
	$(PERMISSIONS)
	@echo "Installation complete."

# Targets
all: check install

.PHONY: all check install
