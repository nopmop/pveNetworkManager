import subprocess
import time
import logging
import logging.handlers
from config import SYSLOG_NAME, DEBUG, TIMEOUT

# Configure logging to syslog
logger = logging.getLogger(SYSLOG_NAME)
logger.setLevel(logging.INFO)
syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
formatter = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)

def run(interface, state, command):
	if DEBUG:
		for c in ["ip", "iptables", "brctl", "service"]:
			if command[:len(c)] == c:
				debug_info(interface, state, "PRE", c)
				result = _run(interface, state, command)
				debug_info(interface, state, "POST", c)
				return result
	else:
		return _run(interface, state, command)

def _run(interface, state, command):
	try:
		result = subprocess.check_output(command, shell=True, text=True).strip()
		if '\n' in result:
			result = '\n' + "\n".join(f"      {line}" for line in result.splitlines())
		logger.info(f"[Context: {interface}/{state}] Exec: '{command}' -- Output: {result}")
		return result
	except subprocess.CalledProcessError as e:
		logger.info(f"[Context: {interface}/{state}] Exec: '{command}' -- Failed (probably ok) with: {e}")
		return ""

def debug_info(interface, state, pre_or_post, command):
	if command == "ip":
		logger.info(f"[Context: {interface}/{state}]  ====================== {pre_or_post} ROUTES ======================")
		_run(f"ip route show")
	if command == "iptables":
		logger.info(f"[Context: {interface}/{state}]  ====================== {pre_or_post} IPTABLES ======================")
		_run(f"iptables -v -L -t nat -n --line-numbers")
		_run(f"iptables -v -L -n --line-numbers")
	if command == "brctl":
		logger.info(f"[Context: {interface}/{state}]  ====================== {pre_or_post} BRIDGES ======================")
		_run(f"brctl show")
	
def run_wait(interface, state, command, search_string, timeout=TIMEOUT, interval=1):
	logger.info(f"[Context: {interface}/{state}] Running command and waiting for: {search_string}...")
	start_time = time.time()	
	while True:
		# Execute the command and capture the output
		try:
			result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
			output = result.stdout
		except subprocess.CalledProcessError as e:
			output = e.output
			logger.info(f"[Context: {interface}/{state}] Still waiting... (command failed with: {e})")

		# Check if the search_string is in the output
		if search_string in output:
			logger.info(f"[Context: {interface}/{state}] Found: '{search_string}' in command output.")
			return output
		
		# Check if the timeout has been exceeded
		elapsed_time = time.time() - start_time
		if elapsed_time > timeout:
			logger.error(f"[Context: {interface}/{state}] Timeout of {timeout} waiting for: {search_string} in command {command}")
			return False
		
		# Wait for the specified interval before running the command again
		time.sleep(interval)

def dhcp_change_iface(interface, state, dhcp_interface, file_path):
	_dhcp_change_iface(interface, state, dhcp_interface, file_path)
	_run(interface, state, f"service isc-dhcp-server restart")

def _dhcp_change_iface(interface, state, dhcp_interface, file_path):
	with open(file_path, 'r') as file:
		lines = file.readlines()

	for i, line in enumerate(lines):
		if line.startswith('INTERFACESv4='):
			# Extract the existing interfaces
			current_interfaces = line.split('=')[1].strip().strip('"')
			interfaces_list = current_interfaces.split()
			logger.info(f"[Context: {interface}/{state}] Found DHCP interfaces: {interfaces_list}")

			if state == 'up' and dhcp_interface not in interfaces_list:
				# Add the new dhcp_interface
				interfaces_list.append(dhcp_interface)
			if state == 'down' and dhcp_interface in interfaces_list:
				# Remove the dhcp_interface
				interfaces_list.remove(dhcp_interface)

			logger.info(f"[Context: {interface}/{state}] New DHCP interfaces: {interfaces_list}")
			# Update the line with the new interfaces list
			new_interfaces = ' '.join(interfaces_list)
			lines[i] = f'INTERFACESv4="{new_interfaces}"\n'
			break

	with open(file_path, 'w') as file:
		file.writelines(lines)
