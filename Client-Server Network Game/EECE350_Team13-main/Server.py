from socket import *
from datetime import datetime
from random import *


def PLAYER(n): #RA
    #this function is used to acquire the players that the user decided on and accept them into the game before it starts.
    for i in range(n): #RA
        L[i],addr=serverSocket.accept() #RA
        #communication sockets with the client formed by the server to accept the players into the game. The server will accept the players consecutively.
        L[i].settimeout(10) #JK
        #set a timeout of 10 seconds for the communication socket to finish its task of sending number. 
        if i+1!=n: #RA
            welcome="Welcome to the game developed by team 13!\nYou are player number "+str(i+1)+" and we are still waiting for "+str(n-i-1)+" players to connect, get ready!"
        #Before reaching n which is the number of the last player set by the user, send a welcome message to each player one after the other.
        #We start from i+1 to display the first player as player 1 and not player 0.
        else: #RA
            welcome="Welcome to the game developed by team 13!\nYou are player number "+str(i+1)+". \nThe game will start soon." #RA
        #Welcome the last player and alert it that the game will start shortly
        L[i].send(welcome.encode()) #RA
        #Send the welcome message to the communication socket.
        print("Player ",(i+1)," has connected.") #RA
        #After sending the welcome message,display to the user that the server has established connection with the players and is ready to start the game.
    print("Connected to all the players. The game will start now.") #RA
    return #RA

def game(n,L): # NM
    #n is an integer that represents the number of players in the game.
    # L is a list of connections to the players. It is assumed that each element of the list L represents a connection to a player.
    #The purpose of this function is to implement a simple game that consists of 3 rounds. 
    # Each round, the players are asked to send a random number between 0 and 9 to the server. 
    # The server measures the round trip time (RTT) between when the server sends the request and when the server receives the response. 
    # The player with the fastest response earns a point. 
    # The player with the most points at the end of the 3 rounds wins the game.
    round1=[]   # NM Create 3 empty lists for each round.
    round2=[]   # NM
    round3=[]   # NM
    scores={} # NM Create a dictionary called scores with the keys being the player numbers and the values being the initial score of 0.
    for i in range(1,n+1):# NM
        scores[i]=0 #NM
    for i in range(n): # NM
        #For each player, send a random number and measure the RTT.
        x=str((randint(0, 9))) #NM 
        L[i].send(x.encode()) #NM
        timeSent=(str(datetime.now())) # NM Here we are creating a timestamp in string format using the current date and time. It's using the datetime module to get the current date and time and then converting it to a string.
        try: #NM
            #Here we try to receive data from a socket connection at index i in the list L. It's trying to receive up to 1024 bytes of data and then decoding it from bytes to a string using the decode() method. 
            #If there is no data to receive or an error occurs, the code will move to the except block.
            answer=L[i].recv(1024).decode() #NM 
            
        except: #NM
            #This block of code is executed if an exception occurs in the try block. 
            #Specifically, it's checking if the socket connection has timed out. 
            #If it has, it will print a message to the console saying that the player at index i+1 has timed out. 
            #It will then call a function called forceFinish() that we wrote down with arguments i and L, that will tell the other players that the game must end. 
            print('Player ',i+1,' has timed out.' ) #NM
            forceFinish(i,L) #NM
            return #NM
            #Finally, it will exit the game function with a return statement in order to end the game.
        timeReceived=(str(datetime.now()))# NM This line is also creating a timestamp in string format using the current date and time. 
        #It's using the datetime module to get the current date and time and then converting it to a string. The same way we used before.
        if float(timeReceived[-9:-1])<10 and float(timeSent[-9:-1])>50: #NM
            #This line is checking if the difference between the last two digits of the timeReceived and timeSent timestamps is greater than 50. 
            # This is done to handle a case where the time changes from one minute to another during the communication. 
            # If the difference is greater than 50, it means that the current communication is part of the previous minute, so the start time is set to 60 seconds before the timeSent timestamp.
            start=float(timeSent[-9:-1])-60 #NM
            #This line sets the start time for measuring RTT based on the previous line's condition. 
            # If the current communication is part of the previous minute, the start time is set to 60 seconds before the timeSent timestamp. 
            end=float(timeReceived[-9:-1]) # NM This line sets the end time for measuring RTT as the last two digits of the timeReceived timestamp
        else: # NM
            start=float(timeSent[-9:-1]) #NM
            end=float(timeReceived[-9:-1]) #NM
        rtt=end-start # NM This line calculates the round trip time as the difference between the end and start times.
        if answer==x: #NM
            round1.append((rtt,i+1)) #NM
        # This line checks if the answer received from the socket connection is equal to a variable x. 
        # If it is, then the tuple (rtt,i+1) is appended to a list called round1. 
        # The tuple contains the measured RTT and the player's index i+1. 
        # Otherwise, (float('inf'),i+1) is appended, which represents an infinite RTT due to an incorrect answer.
        else: # NM
            round1.append((float('inf'),i+1)) #NM
    results1=round1.copy() # NM
    results1.sort() # NM here we sort the results
    send1='\nPodium for round 1:\n' # NM This line creates a string called send1 with a message about the results of round 1. Here we send the results of the winner.
    for i in range(len(results1)): #NM 
        if results1[i][0]!=float('inf'): # NM We check if the RTT of the current player (at index i) is finite, meaning they answered correctly.
# We append a string to the send1 variable summarizing the performance of the current player. The string includes the player's index (i+1), (results1[i][1]), and their RTT (results1[i][0]).
            send1+='Number '+str(i+1)+": Player "+str(results1[i][1])+' with '+str(results1[i][0])[:7]+" seconds.\n" #NM
        else: #NM
            send1+='Number '+str(i+1)+": Player "+str(results1[i][1])+' disqualified.\n' # NM if its infinity means incorrect we disqualify. #NM
    if results1[0][0]!=float('inf'): #NM
        scores[results1[0][1]]+=1 #NM
        #This line increments the score of the winning player (identified by their index results1[0][1]) in scores dictionary.
        send1+='\nThe winner of this round is '+ "Player "+str(results1[0][1]) + ".\n" #NM
    else: #NM
        #This line appends a string to send1 to indicate that there were no winners for the round.
        send1+="\nThere are no winners for this round.\n" #NM
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)#NM Create a new list of tuples to store the new scores after the round results and sort it in reverse order to get from highest to lowest score
    send1+="\nCummulative scores:\n"#NM add the display to the results that will be sent
    for player, score in sorted_scores:
        if score != 0:#NM if the score is different than zero, it won't show in the results
            send1+= "Player "+str(player)+' : '+str(score)+' \n'#NM add it to send2 for the display to the client
    for i in range(n): #NM
        L[i].send(send1.encode()) #NM
    for i in range(n): #NM
        #For each player, send a random number and measure the RTT.
        x=str((randint(0, 9))) #NM
        L[i].send(x.encode()) #NM
        timeSent=(str(datetime.now())) # NM Here we are creating a timestamp in string format using the current date and time. It's using the datetime module to get the current date and time and then converting it to a string.
        try: #NM
            #Here we try to receive data from a socket connection at index i in the list L. It's trying to receive up to 1024 bytes of data and then decoding it from bytes to a string using the decode() method.
            #If there is no data to receive or an error occurs, the code will move to the except block.
            answer=L[i].recv(1024).decode() #NM
        except: #NM
            #This block of code is executed if an exception occurs in the try block. 
            #Specifically, it's checking if the socket connection has timed out. 
            #If it has, it will print a message to the console saying that the player at index i has timed out. 
            #It will then call a function called forceFinish() that we wrote down with arguments i and L. 
            print('Player ',i+1,' has timed out.' ) #NM
            forceFinish(i,L) #NM
            return # NM Finally, it will exit the function with a return statement.
        timeReceived=(str(datetime.now())) # NM This line is also creating a timestamp in string format using the current date and time. 
       #It's using the datetime module to get the current date and time and then converting it to a string. The same way we used before.
        if float(timeReceived[-9:-1])<10 and float(timeSent[-9:-1])>50: # NM 
            #This line is checking if the difference between the last two digits of the timeReceived and timeSent timestamps is greater than 50. 
            # This is done to handle a case where the time changes from one minute to another during the communication. 
            # If the difference is greater than 50, it means that the current communication is part of the previous minute, so the start time is set to 60 seconds before the timeSent timestamp. 
            start=float(timeSent[-9:-1])-60 # NM This line sets the start time for measuring RTT based on the previous line's condition. 
            end=float(timeReceived[-9:-1])#  NM 
        else: # NM 
            start=float(timeSent[-9:-1]) # NM 
            end=float(timeReceived[-9:-1])# NM 
        rtt=end-start# NM 
        #The RTT is timeReceived-timeSent
        if answer==x: # NM 
            round2.append((rtt,i+1))# NM 
        # This line checks if the answer received from the socket connection is equal to a variable x. 
        # If it is, then the tuple (rtt,i+1) is appended to a list called round1. 
        # The tuple contains the measured RTT and the player's index i+1. 
        # Otherwise, (float('inf'),i+1) is appended, which represents an infinite RTT due to an incorrect answer.
        else: # NM 
            round2.append((float('inf'),i+1))# NM 
    results2=round2.copy()# NM 
    results2.sort() # NM here we sort the results
    send2='\nPodium for round 2:\n' # NM This line creates a string called send2 with a message about the results of round 2. Here we send the results of the winner.
    for i in range(len(results2)): # NM We check if the RTT of the current player (at index i) is finite, meaning they answered correctly.
# We append a string to the send2 variable summarizing the performance of the current player. 
#The string includes the player's index (i+1), (results2[i][1]), and their RTT (results2[i][0]).
        if results2[i][0]!=float('inf'): # NM 
            send2+='Number '+str(i+1)+": Player "+str(results2[i][1])+' with '+str(results2[i][0])[:7]+" seconds.\n"# NM 
        else:# NM 
            send2+='Number '+str(i+1)+": Player "+str(results2[i][1])+' disqualified.\n' # NM if its infinity means incorrect we disqualify.
    if results2[0][0]!=float('inf'):# NM 
        scores[results2[0][1]]+=1  # NM This line increments the score of the winning player (identified by their index results2[0][1]) in scores dictionary.
        send2+='\nThe winner of this round is '+ "Player "+str(results2[0][1]) + ".\n"# NM 
    else:# NM 
        #This line appends a string to send1 to indicate that there were no winners for the round.
        send2+="\nThere are no winners for this round.\n"# NM 
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)#NM Create a new list of tuples to store the new scores after the round results and sort it in reverse order to get from highest to lowest score
    send2+="\nCummulative scores:\n"#NM add the display to the results that will be sent
    for player, score in sorted_scores:
        if score != 0:#NM if the score is different than zero, it won't show in the results
            send2+= "Player "+str(player)+' : '+str(score)+' \n'#NM add it to send2 for the display to the client
    for i in range(n):# NM 
        L[i].send(send2.encode())# NM 
    for i in range(n):# NM 
        x=str((randint(0, 9)))# NM 
        #For each player, send a random number and measure the RTT.
        L[i].send(x.encode())# NM 
        timeSent=(str(datetime.now())) # NM Here we are creating a timestamp in string format using the current date and time. It's using the datetime module to get the current date and time and then converting it to a string.
        try:# NM 
            #Here we try to receive data from a socket connection at index i in the list L. It's trying to receive up to 1024 bytes of data and then decoding it from bytes to a string using the decode() method. 
           #If there is no data to receive or an error occurs, the code will move to the except block.
            answer=L[i].recv(1024).decode()# NM 
        except:# NM 
            #This block of code is executed if an exception occurs in the try block. 
            #Specifically, it's checking if the socket connection has timed out. 
            #If it has, it will print a message to the console saying that the player at index i has timed out. 
            #It will then call a function called forceFinish() that we wrote down with arguments i and L. 
            print('Player ',i+1,' has timed out.' )# NM 
            forceFinish(i,L)# NM 
            return # NM Finally, it will exit the function with a return statement.
        timeReceived=(str(datetime.now())) # NM This line is also creating a timestamp in string format using the current date and time. 
        #It's using the datetime module to get the current date and time and then converting it to a string. The same way we used before.
        if float(timeReceived[-9:-1])<10 and float(timeSent[-9:-1])>50:# NM 
            #This line is checking if the difference between the last two digits of the timeReceived and timeSent timestamps is greater than 50. 
           # This is done to handle a case where the time changes from one minute to another during the communication. 
           # If the difference is greater than 50, it means that the current communication is part of the previous minute, so the start time is set to 60 seconds before the timeSent timestamp.
            start=float(timeSent[-9:-1])-60# NM 
            #This line sets the start time for measuring RTT based on the previous line's condition. 
            # If the current communication is part of the previous minute, the start time is set to 60 seconds before the timeSent timestamp. 
            end=float(timeReceived[-9:-1])# NM 
        else:# NM 
            start=float(timeSent[-9:-1])# NM 
            end=float(timeReceived[-9:-1])# NM 
        rtt=end-start# NM 
        if answer==x:# NM 
            round3.append((rtt,i+1))# NM 
            # This line checks if the answer received from the socket connection is equal to a variable x. 
            # If it is, then the tuple (rtt,i+1) is appended to a list called round1. 
            # The tuple contains the measured RTT and the player's index i+1. 
            # Otherwise, (float('inf'),i+1) is appended, which represents an infinite RTT due to an incorrect answer.
        else:# NM 
            round3.append((float('inf'),i+1))# NM 
    results3=round3.copy()# NM 
    results3.sort()# NM 
    send3='\nPodium for round 3:\n'# NM 
    for i in range(len(results3)):# NM 
        if results3[i][0]!=float('inf'):  # NM We check if the RTT of the current player (at index i) is finite, meaning they answered correctly.
# We append a string to the send3 variable summarizing the performance of the current player. The string includes the player's index (i+1), (results3[i][1]), and their RTT (results3[i][0]).
            send3+='Number '+str(i+1)+": Player "+str(results3[i][1])+' with '+str(results3[i][0])[:7]+" seconds.\n"# NM 
        else:# NM 
            send3+='Number '+str(i+1)+": Player "+str(results3[i][1])+' disqualified.\n'# NM 
            
    if results3[0][0]!=float('inf'):# JK
        scores[results3[0][1]]+=1# JK 
        #This line increments the score of the winning player (identified by their index results3[0][1]) in scores dictionary.
        send3+='\nThe winner of this round is '+ "Player "+str(results3[0][1]) + ".\n\n" # JK 
    else:# JK 
        #This line appends a string to send1 to indicate that there were no winners for the round.
        send3+="\nThere are no winners for this round.\n\n"# JK 
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)#NM Create a new list of tuples to store the new scores after the round results and sort it in reverse order to get from highest to lowest score
    send3+="\nCummulative scores:\n"#NM add the display to the results that will be sent
    for player, score in sorted_scores:
        if score != 0:#NM if the score is different than zero, it won't show in the results
            send3+= "Player "+str(player)+' : '+str(score)+' \n'#NM add it to send2 for the display to the client
    send3+="\n"
    finalScore= [(v, k) for k, v in scores.items()]# JK Turns the dictionnary of Key=player number and value=score to a list of tuples with (score,player number)
    finalScore.sort(reverse=True)# JK sort it in reverse order in order to have the one with the highest score first
    if len(finalScore)==1 or finalScore[0][0]!=finalScore[1][0]:# JK Checks if the first player (winner) doesnt have the same score that the second
        #So if it is the case where we have only one winner
        send3+="Player "+ str(finalScore[0][1]) + " has won the game for having the highest score which is: "+str(finalScore[0][0])# JK add it to the round 3 results
    elif (finalScore[0][0]==finalScore[1][0]) and (len(finalScore)==2 or finalScore[2][0]!=finalScore[1][0]):# JK Checks if the winner has the same score as the second player, and different than the third
        #And if yes it sends the necessary information, so it's the case for 2 winners
        print("Two winners case.")# JK 
        draw1=finalScore[0][1]# JK Gets the number of the first player
        draw2=finalScore[1][1]# JK Gets the number of the second player
        scoreDraw1=round1[draw1-1][0]+round2[draw1-1][0]+round3[draw1-1][0]# JK Sum of the three rounds for 1st player
        scoreDraw2=round1[draw2-1][0]+round2[draw2-1][0]+round3[draw2-1][0]# JK Sum of the three rounds for 2nd player
        if scoreDraw1<scoreDraw2:# JK Checks which one has the lowest cummulative time and sends information accordingly
            send3+='Player '+str(draw1)+" has won the game by split decision as he had the same number of wins of player "+str(draw2)+" but had a better overall time."
            #Player 1 winner case
        else:# JK 
            #Player 2 winner case
            send3+='Player '+str(draw2)+" has won the game by split decision as he had the same number of wins of player "+str(draw1)+" but had a better overall time."# JK 
    elif (len(finalScore)>=3 and (finalScore[0][0]==finalScore[1][0] and finalScore[2][0]==finalScore[1][0])):# JK Checks if the 3 first players have the same score
        #And if yes, it sends necessary information
        print("Three winners case.")# JK 
        draw1=finalScore[0][1]# JK Gets the number of the first player
        draw2=finalScore[1][1]# JK Gets the number of the second player
        draw3=finalScore[2][1]# JK Gets the number of the third player
        scoreDraw1=round1[draw1-1][0]+round2[draw1-1][0]+round3[draw1-1][0]# JK Sum of the three rounds for 1st player
        scoreDraw2=round1[draw2-1][0]+round2[draw2-1][0]+round3[draw2-1][0]# JK Sum of the three rounds for the 2nd player
        scoreDraw3=round1[draw3-1][0]+round2[draw3-1][0]+round3[draw3-1][0]# JK Sum of the three rounds for the 3rd player
        if scoreDraw1<scoreDraw2 and scoreDraw1<scoreDraw3:# JK Player 1 winner case
            send3+='Player '+str(draw1)+" has won the game by split decision as he had the same number of wins of player "+str(draw2)+" and player "+str(draw3)+" but had a better overall time."# JK
        elif scoreDraw2<scoreDraw1 and scoreDraw2<scoreDraw3:# JK Player 2 winner case
            send3+='Player '+str(draw2)+" has won the game by split decision as he had the same number of wins of player "+str(draw1)+" and player "+str(draw3)+" but had a better overall time." # JK
        else:#Player 3 winner case JK 
            send3+='Player '+str(draw3)+" has won the game by split decision as he had the same number of wins of player "+str(draw2)+" and player "+str(draw1)+" but had a better overall time."# JK 
            
    for i in range(n):# JK 
        L[i].send(send3.encode())#Sends the final results# JK 
    
    return#Ends the function

def forceFinish(n,L): # JK
    #this function sends a message to the connected clients telling them that a player has disconnected. It is used within the game function.
    finish="FINISH"# JK
    for i in range(len(L)):# JK
        L[i].send(finish.encode())# JK
        #send a message to the client to finish immediately. when the client receives FINISH it will know that the game has ended and stop running it. 
    return# JK
    
def close(n):# RA
    #closing the communication socket is essential since without this function the resouces will remain in the system leading to leaks in the memory and bugs in the code.
    serverSocket.close()# RA close the server socket
    for i in range(n):# RA
        L[i].close()# RA
    #close the communication sockets consecutively once the player is done with its task.
    print("The game has ended.")# RA


serverName = gethostname()#Get the IP address of the local machine.# RA
serverSocket=socket(AF_INET, SOCK_STREAM)# RA create the server socket.We decided to use TCP for the socket as we need reliability in order to receive all the answers from the players without need to worry about it.
serverSocket.bind((serverName,350))# RA Bind a socket to port 350
number=int(input("Please enter the number of players: "))#RA The number of players is chosen by the user.
serverSocket.listen(1)#RA Listen for incoming connections and connect to the first one.
L=[]# RA
for i in range(number):# RA Create a list L of size number which contains the name of all the players, which will later be used as the name for the socket connection
    temp='player'+str(i)# RA 
    L.append(temp)# RA 
PLAYER(number)#RA This function is used to connect to all the client before starting the game
game(number,L)#RA This function manages the game for 3 rounds
close(number)#RA This function is used to close all connections to clients when the game has ended
    


