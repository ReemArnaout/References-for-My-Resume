from socket import *
from datetime import datetime


def game(): # CZ 
    number=clientSocket.recv(1024).decode()# CZ Receive the random number from the server
    if number=="FINISH":# CZ Handling the case were the player disconnects.
        print("A player has disconnected, the game will shut down.")# CZ print output for the client
        return# CZ End the function if it is the case of a disconnection
    disp="Type the number "+number+" as fast as you can : "# CZ Taking an input of the number the client is entering
    x=str(input(disp))# CZ The actual input
    clientSocket.send(x.encode())# CZ Encoding and sending the response back to the server
    results=clientSocket.recv(1024).decode()# CZ Receiving the results from the server
    print(results)# CZ Printing results
    number=clientSocket.recv(1024).decode()# CZ Receive the random number from the server
    if number=="FINISH":# CZ Handling the case were the player disconnects.
        print("A player has disconnected, the game will shut down.")# CZ print output for the client
        return# CZ End the function if it is the case of a disconnection
    disp="Type the number "+number+" as fast as you can : "# CZ Taking an input of the number the client is entering
    x=str(input(disp))# CZ The actual input
    clientSocket.send(x.encode())# CZ Encoding and sending the response back to the server
    results=clientSocket.recv(1024).decode()# CZ Receiving the results from the server
    print(results)# CZ Printing results
    number=clientSocket.recv(1024).decode()# CZ Receive the random number from the server
    if number=="FINISH":# CZ Handling the case were the player disconnects.
        print("A player has disconnected, the game will shut down.")# CZ print output for the client
        return# CZ End the function if it is the case of a disconnection
    disp="Type the number "+number+" as fast as you can : "# CZ Taking an input of the number the client is entering
    x=str(input(disp))# CZ The actual input
    clientSocket.send(x.encode())# CZ Encoding and sending the response back to the server
    results=clientSocket.recv(1024).decode()# CZ Receiving the results from the server
    print(results)# CZ Printing results

serverName = gethostname()# CZ Gett the local machine IP address
clientSocket = socket(AF_INET, SOCK_STREAM)# CZ using TCP for reliability
clientSocket.connect((serverName,350))# CZ Connecting to port 350
welcome=clientSocket.recv(1024).decode()# CZ Receive the welcome message from the server
print(welcome)# CZ print the welcome message
game()# CZ Run the game function which will manage the game

