import socket
import psutil
import pickle
import ipaddress
import concurrent.futures
try:
    from server.packet import Packet, PacketType
except ModuleNotFoundError:
    from packet import Packet, PacketType

# The port to scan for
PORT = 5445
# Timeout for the connection attempt
TIMEOUT = 1
# Number of threads to limit the max parallel scans
MAX_THREADS = 100

def get_local_ip():
    """
    Get the local IP address of the machine.
    """
    return socket.gethostbyname(socket.gethostname())

def get_subnet():
    """
    Get the subnet of the local network by finding the local IP address and subnet mask.
    """
    # Get network interfaces info using psutil
    interfaces = psutil.net_if_addrs()
    
    # We'll use 'eth0' for wired or 'wlan0' for Wi-Fi, you can adjust based on your system.
    for interface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                local_ip = addr.address
                netmask = addr.netmask
                
                # If both IP and netmask found, compute the subnet
                if local_ip and netmask:
                    return local_ip, netmask
    return None, None

def get_subnet_network(local_ip, netmask):
    """
    Calculate the subnet network from IP and netmask.
    """
    network = ipaddress.IPv4Network(f'{local_ip}/{netmask}', strict=False)
    return network

def scan_ip(ip):
    """
    Try to connect to a given IP on port 5555.
    """
    try:
        # Create a socket object and set a timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)

        # Attempt to connect to the given IP and port
        result = sock.connect_ex((str(ip), PORT))
    
        if result == 0:
            # get info about the server
            sock.recv(2048) # throw the "connection received" message out
            sock.send(pickle.dumps(Packet(PacketType.GET, {"type": "INFO"})))
            response = pickle.loads(sock.recv(2048))

            sock.send(pickle.dumps(Packet(PacketType.DISCONNECT,None)))
            sock.close()

            data = response.data
            data["ip"] = str(ip)

            return data
    except socket.error:
        pass  # Ignore errors when trying to connect
    return False

def scan_network(network):
    """
    Scan the entire network for open TCP servers on port 5555.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Submit tasks to the executor for all IPs
        futures = {executor.submit(scan_ip, ip): ip for ip in network.hosts()}

        # Process results as they are completed
        for future in concurrent.futures.as_completed(futures):
            ip = futures[future]
            print("Scanning " + str(ip) + "...")
            try:
                result = future.result()
                if result:
                    yield result
            except Exception as e:
                yield f"Error scanning {ip}: {e}"


if __name__ == "__main__":
    local_ip, netmask = get_subnet()
    network = get_subnet_network(local_ip, netmask)

    for server in scan_network(network):
        print("FOUND: " + server)