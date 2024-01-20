from tkinter import *
from socket import *

class GameClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Game Client")
        self.master.geometry("600x500")
        self.master.resizable(False, False)

        self.connect_to_server()

        # Display welcome message
        welcome = self.client_socket.recv(1024).decode()
        self.welcome_label = Label(self.master, text=welcome, font=("Helvetica", 14))
        self.welcome_label.pack(pady=20)

        self.play_game()

    def connect_to_server(self):
        # Connect to server
        serverName = gethostname()
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((serverName, 350))

    def play_game(self):
        self.number_label = Label(self.master, text="", font=("Helvetica", 14))
        self.number_label.pack(pady=10)

        self.number_entry = Entry(self.master, font=("Helvetica", 14))
        self.number_entry.pack(pady=10)
        self.number_entry.focus_set()

        self.send_button = Button(self.master, text="Send", command=self.send_number)
        self.send_button.pack(pady=10)

        self.results_label = Label(self.master, text="", font=("Helvetica", 14))
        self.results_label.pack(pady=10)

        self.number_of_rounds = 3
        self.current_round = 1
        self.play_round()

    def play_round(self):
        self.number_label.config(text="Round " + str(self.current_round) + ": Enter number")
        self.number_entry.delete(0, END)
        self.results_label.config(text="")

        # Receive number from server
        number = self.client_socket.recv(1024).decode()

        # Check if the game is finished
        if number == "FINISH":
            self.number_label.config(text="Game Over")
            self.number_entry.config(state=DISABLED)
            self.send_button.config(state=DISABLED)
            self.master.after(30000, self.master.quit)
            return

        # Display number to user
        self.number_label.config(text="Round " + str(self.current_round) + ": " + number)

        # Bind Enter key to send button
        self.master.bind('<Return>', lambda event: self.send_button.invoke())

    def send_number(self):
        # Get number from user
        x = self.number_entry.get()

        # Send number to server
        self.client_socket.send(x.encode())

        # Receive results from server
        results = self.client_socket.recv(1024).decode()

        # Display results to user
        self.results_label.config(text=results)

        self.current_round += 1

        # Play next round
        if self.current_round <= self.number_of_rounds:
            self.play_round()
        else:
            # Game finished, wait for 30 seconds before quitting
            self.master.after(30000, self.master.quit)

root = Tk()
game_client = GameClient(root)
root.mainloop()
