# EECE350_Team13
This is a game developed by Nader Al Masri, Reem Arnaout, Julien Kanaan and Christopher Zeitoun

You can access the HIGH RESOLUTION video using the following link: https://mailaub-my.sharepoint.com/:v:/g/personal/nma119_mail_aub_edu/EXCq4yZHMy9Nu1h3o2nhMbEBKUe8a8FSVH2ob4-urG9cYA?e=co01Ki

# Please note that we made some updates to the code after we uploaded the video, such as cumalative scores.

Concerning the project, we uploaded a client and a server py files for running the game using a normal console; and we uploaded a version of the code with an interface.

To run the code using the interface, first you should run the server on a console (cmd) and input number of players, and run the client separately on 2 different consoles and then you will get the app interface.

Overview of the game:


This code implements a multiplayer game where each player has to quickly input a number sent by the server. The game consists of three rounds and the players are ranked based on their reaction time in each round.

The game() function in the server code implements the game. It starts by generating a random number between 0 and 9 and sending it to each player. Then, it receives the input from each player and calculates the round-trip time (RTT) between sending and receiving the number. If the input matches the sent number, the (RTT, player number) tuple is appended to the corresponding round list (round1, round2, or round3). Otherwise, the tuple (inf, player number) is appended, indicating that the player was disqualified for that round. After processing all players' inputs for each round, the tuples are sorted based on the RTT, and the function generates a podium string to send to the players with the ranking and RTT of each player.

The PLAYER(n) function in the server code waits for n players to connect to the server, creates a socket for each player, sends a welcome message, and returns a string indicating that all players are connected.

The client code connects to the server, receives the welcome message, and calls the game() function to start playing. For each round, the client receives a number from the server, prompts the user to input the number as fast as possible, sends the input to the server, receives the results, and prints them.

However, there are several issues with this code that we were able to resolve. One issue is that how to handle a tie. Another issue is waiting for all players to connect and then initiating the game. Also we were able to close the connection when the game fails and when the game finishes using the force finish function. Also, when a player disconnects we were able to force finish the game as indicated in the demo video. Ties of odd and even numbers of players are handled in the code.
