import psutil  # Used for accessing system and network-related information, including active connections.
import time  # Used for managing sleep intervals in the detection loop.
import os  # Used for executing system commands, like shutting down the network interface.

def detect_slowloris(interface, threshold=50, detection_limit=3):
    """Detect potential Slowloris attacks by monitoring open connections."""
    detection_count=0  # Initialize detection counter

    while True:
        connection_counts={}  # Dictionary to hold counts of open connections per IP

        
        for conn in psutil.net_connections(): # Loop through all current network connections

            if conn.status in ['SYN_RECV', 'ESTABLISHED'] and conn.raddr: # Check for connections that are established or in SYN_RECV state 
                ip = conn.raddr[0]  # Get the remote IP address
                connection_counts[ip]=connection_counts.get(ip, 0)+1 # Increment the count of connections for the IP

        # Check each IP address for potential Slowloris attack based on connection count #
        for ip, count in connection_counts.items():
            if count>threshold:  # If open connections exceed the threshold
                print(f"Potential Slowloris attack from {ip} with {count} open connections.")
                detection_count+=1  # Increment the detection count

                
                if detection_count>=detection_limit:    # If the detection limit is reached, shut down the network interface
                    print("Three detections of potential Slowloris attack. Shutting down network interface.")
                    os.system(f"sudo ifconfig {interface} down")  # Shut down the specified network interface
                    print(f"The network interface '{interface}' has been brought down.")
                    print(f"To bring it back up, run: 'sudo ifconfig {interface} up'")
                    print("Code terminated.")
                    return  # Exit the detection script

        time.sleep(10)  # Wait before the next detection cycle

if __name__=="__main__":
    interface='enp0s3'  # Specify the network interface to monitor (change as needed)
    print("Starting Slowloris detection on interface:", interface)
    detect_slowloris(interface, threshold=50, detection_limit=3)  # Start the detection process
