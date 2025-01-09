# NOTES: 
# Code is not sourced from another author
# AI usage: Used ChatGPT for debugging and syntax issues only. 

from scapy.all import * # Scapy is used for packet sniffing, packet dissection, and manipulation. It helps capture DNS traffic and analyze packet layers like IP, DNS, and UDP.                                                                                                                                                        
import os   # The os library allows interaction with the operating system, such as executing system commands (here used for shutting down the network interface).                                                                                         
import sys  # The sys library is needed for exiting the script after blocking DNS traffic and handling script termination.                                                                                      

# Parameters #

monitor_duration=10 # Duration to monitor traffic (in seconds)
response_warning_interval=100  # Interval for high volume DNS responses warning
spoofing_warning_interval=100  # Interval for IP spoofing warning
packet_limit=1500  # Limit of DNS packets received before shutting down network interface

# Tracking DNS requests made by Ubuntu #

ubuntu_requests=set() # DNS Requests Made by Ubuntu
response_count=0    # Total DNS Responses Received
dns_packet_count=0  # Total DNS packets Received

# Counters for warnings #

dns_response_warning_count=0 
ip_spoofing_warning_count=0

# Flag to indicate if DNS traffic is blocked #

dns_blocked=False

# Function to block DNS traffic after 1500 response packets #

def block_dns():
    global dns_blocked
    if not dns_blocked:  # Only block if not already blocked
        print("Stopping Acceptance of incoming DNS traffic")
        os.system("sudo ifconfig enp0s3 down")  # Block DNS traffic by shutting down interface
        dns_blocked = True
        print("Blocked incoming DNS traffic")
        print("!! To allow DNS traffic again, run the following command: ")
        print("sudo ifconfig enp0s3 (or your interface) up")
        sys.exit("Exiting Script after blocking DNS traffic.")

# Handling of DNS requests and responses #

def packet_handler(packet):
    global response_count, dns_response_warning_count, ip_spoofing_warning_count, dns_packet_count

    
    if packet.haslayer(IP) and packet.haslayer(DNS) and packet.haslayer(UDP): # Check if the packet has IP and DNS layers 
        dns_packet_count+=1  # Increment the total DNS packet count

        if packet[DNS].qr==1: # Check if it's a DNS response
            response_count+=1
            response_ip=packet[IP].src  # Source of the response
            dest_ip=packet[IP].dst      # Destination of the response (e.g., Ubuntu)

            if dest_ip not in ubuntu_requests:  # Check if Ubuntu did not send a request
                ip_spoofing_warning_count+=1
                if ip_spoofing_warning_count % spoofing_warning_interval==0: # Found 1 spoofed packet
                    print(f"Warning: IP spoofing detected! DNS response sent to {dest_ip} from {response_ip}, but no request was made by {dest_ip}.")

            if response_count % response_warning_interval==0: # Check if high volume of DNS responses has been received
                dns_response_warning_count+=1
                print(f"Warning: High volume of DNS responses received! Count: {response_count}")

        if dns_packet_count >= packet_limit:    # Check if the packet count exceeds the limit
            block_dns()  # Call the function to block DNS traffic

# Track DNS requests made by Ubuntu #

def request_handler(packet):
    
    if packet.haslayer(IP) and packet.haslayer(DNS) and packet.haslayer(UDP):   # Check if the packet has IP and DNS layers
        if packet[DNS].qr == 0:  # Is DNS request
            source_ip = packet[IP].src
            if source_ip == 'Ubuntu_IP':  # Replace with actual Ubuntu IP
                ubuntu_requests.add(source_ip)

def monitor_traffic(interface):
    print("Monitoring for DNS amplification and IP spoofing")
    
    while True: # Start sniffing packets 
        sniff(iface=interface, prn=packet_handler, timeout=1)

if __name__ == "__main__":  # This checks if the script is being run directly. If true, it executes the code inside the block.
    interface = 'enp0s3'  # Change to your interface (eth0 if kali)
    print("Starting to capture DNS requests and monitor IP spoofing")
    sniff(iface=interface, prn=request_handler, filter="udp port 53", store=0, timeout=monitor_duration)    # Sniff DNS requests (sent by Ubuntu)
    monitor_traffic(interface)  # Sniff DNS responses