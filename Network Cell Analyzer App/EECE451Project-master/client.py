""" import socket
import json

def Main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    
        s.connect(('0.0.0.0', 8080))
        print("Connected . . . .")
        s.send(json.dumps({
        "operator": "Operator 100",
        "signal_power": "20",
        "snr": 30,
        "network_type": "Type 2",
        "frequency_band": "200kHz",
        "cell_id": "1234",
        "date_1": None,
        "date_2": None
        }).encode())
        data = s.recv(1024).decode('utf-8')
        print('Received from server: ' + data)

        s.send(json.dumps({
        "operator": "Operator 20",
        "signal_power": "30",
        "snr": 10,
        "network_type": "Type 3",
        "frequency_band": "100kHz",
        "cell_id": "123456789",
        "date_1": "2024-04-12 1:00:00",
        "date_2": "2024-04-14 13:00:00"
        }).encode())
        data = s.recv(1024).decode('utf-8')
        print('Received from server: ' + data)

        s.close()

if __name__ == '__main__':
    Main() """

import socket

# Define the server address and port
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 8080

# Define the data to send
data = '{"operator": "test", "signal_power": "20", "snr": "10", "network_type": "LTE", "frequency_band": "5G", "cell_id": "12345"}'

# Define the number of clients to simulate
NUM_CLIENTS = 5

# Create and connect multiple client sockets
for _ in range(NUM_CLIENTS):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
    print("Connected to server")

    # Send data to the server
    client_socket.sendall(data.encode())
    print("Data sent to server")

    # Receive response from the server
    response = client_socket.recv(1024)
    print("Response from server:", response.decode())

    # Close the client socket
    client_socket.close()
