# Server Implementation
# Implementation of the server_handler 
# Michael Long, Gennadii Sytov
# CS494 Final Project, June 2019

# Imports / Constants
import socket
import _thread

BUFFER = 1024 # Defines the maximum byte size of input from a client

class server_handler():

    def __init__(self, host, port):
        print("Server is initializing")
        # Basic socket setup
        self.host = host
        self.port = port
        self.address = (host, port)
        # Attempt to bind to socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)
        # Data
        self.users = {} # Key is a user name, value is an address
        self.rooms = {} # Key is a room name, value is a list of users in the room
        self.rooms['General'] = [] # Server generates with a default room
        self.user_count = 0
        # commands, commands_usage, and commands_desc are lists to make adding new commands easier without modifying the '/?' command
        self.commands = ['/create ', '/join ', '/leave ', '/users', '/users ', '/list', '/s ', '/w ', '/disconnect']
        self.commands_usage = ['room_name', 'room_name . . . room_name', 'room_name', '', 'room_name', '', 'room_name . . . room_name message', 'username message', '']
        self.commands_desc = ['create new room', 'joins each room_name', 'leaves room_name', 'list all users', 'list all users in room_name', 'list all rooms', 'send message to each room_name', 'send message to user', 'disconnect from the server']
        print("Server is done initializing")

    def connect(self, connection):

        connected = True

        try:
            # Add user, get a username to place into data structure
            connection.send(bytes("Successfully connected to the Server", "utf8"))
            connection.send(bytes("Please enter a unique username: ", "utf8"))
            username = connection.recv(BUFFER).decode("utf8")

            # Check for null information sent in the connection buffer
            if username == '':
                print("Error: Detected null user, closing thread")
                return
            
            print("Beginning check in user process")
            # First user, no possibility of duplicates
            if (self.user_count == 0):
                print("First user has connected")
                self.user_count += 1
            else:
                # Test for duplicate usernames
                flag_entered = False
                flag_repeat = False
                for check in self.users.keys():
                    if check == username:
                        flag_repeat = True

                # Duplicate username detected, keep checking until a unique username is given
                while flag_repeat:
                    connection.send(bytes("Username is taken, please enter a valid username: ", "utf8"))
                    username = connection.recv(BUFFER).decode("utf8")
                    flag_repeat = False
                    for check in self.users.keys():
                        if check == username:
                            flag_repeat = True

            # Once a username has been established, welcome and print a series of commands
            connection.send(bytes("Welcome " + username + " type /? for a list of commands", "utf8"))
            self.rooms['General'].append(username)
            connection.send(bytes("You have joined the room: General", "utf8"))
            # Assign User Info
            self.users[username] = connection
            print(self.users[username])
            print("End check in user process")

            try:

                while connected:

                    print("Waiting for input from: " + username)
                    # Receive a message from a user
                    data = connection.recv(BUFFER)
                    scrub_data = data.decode("utf8")
                    # Check for '/' to determine if there is a command

                    if scrub_data[0] == '/':
                        print("Received a '/' command from: " + username)
                        # Translate to determine command
                        text = scrub_data.split()
                        print("Data sent from: " + username)
                        for to_print in text:
                            print(to_print)
                        # List set of commands 
                        if text[0] == "/?":
                            for (print_command, print_usage, print_desc) in zip(self.commands, self.commands_usage, self.commands_desc):
                                if print_command == self.commands[0] or print_command == self.commands[len(self.commands)-1]:
                                    connection.send(bytes(print_command + print_usage + ", " + print_desc, "utf8"))
                                else:
                                    connection.send(bytes(print_command + print_usage + ", " + print_desc + '\n', "utf8"))

                        # Add a user to one or more rooms
                        elif text[0] == "/join" and len(text) > 1:

                            # Parse the message from left to right until it doesn't match a room name
                            print(username + " may want to send to multiple rooms, doing a parse")
                            parse = text[1::] #get rid of /join
                            rooms_to_join = []

                            # Scan through the list of rooms the user typed until one item doesn't match
                            for check in parse:
                                for room_name, room_check in self.rooms.items():
                                    if check == room_name:
                                        print("Adding to rooms_to_send: " + check)
                                        rooms_to_join.append(room_name)
                                        break
                                print("Back to check in parse loop")
                            
                            # Check if there is at least one room to go through
                            if not rooms_to_join:
                                connection.send(bytes("Error -- room does not exist", "utf8"))
                            else:
                                # Check each room to verify if the user is already in the room and if the room exists
                                for try_room in rooms_to_join:

                                    print(username + " is going to join a room")
                                    flag_dup = True

                                    # Verify the user is not in the room in the room
                                    for check in self.rooms[try_room]:
                                        print("Looking for duplicates: " + check)
                                        if check == username:
                                            flag_dup = False

                                    # If room exists, add the connection to the room
                                    if flag_dup == True:
                                        print("Successfully added to room")
                                        self.rooms[try_room].append(username)
                                        connection.send(bytes("You have joined the room!", "utf8"))
                                    # Room exists, but the user is already in the room
                                    else:
                                        connection.send(bytes("Error -- you're already in the room: " + try_room, "utf8"))
                        
                        # Remove a user from a room
                        elif text[0] == "/leave":
                            if len(text) > 1:
                                print(username + " is going to leave a room")
                                flag = False
                                flag_inroom = False
                                attempt_room = text[1] 
                                # Verify that the room exists
                                for check in self.rooms.keys():
                                    print("Scanning room_list")
                                    if check == attempt_room:
                                        flag = True

                                # Verify the user is in the room
                                if flag == True:
                                    for check in self.rooms[text[1]]:
                                        print("Looking for users in room")
                                        if check == username:
                                            flag_inroom = True

                                # Room exists and the user is in the room, leave the room
                                if flag == True and flag_inroom == True:
                                    print("Successfully left room")
                                    for check in self.rooms[text[1]]:
                                        print(check)
                                    self.rooms[attempt_room].remove(username)
                                    connection.send(bytes("You have left the room!", "utf8"))
                                # Room exists, user is not in the room, error
                                elif flag == True and flag_inroom == False:
                                    connection.send(bytes("Error -- you can't leave a room you're not in", "utf8"))
                                # Room doesn't exist, error
                                else:
                                    connection.send(bytes("Error -- room does not exist", "utf8"))
                            else:
                                connection.send(bytes("Error -- must list at least one room", "utf8"))
                             

                        # Create a new room
                        elif text[0] == "/create":
                            if len(text) > 1:
                                print(username + " is going to create a room")
                                flag = False
                                flag_roomexists = False
                                # Verify that the room doesn't exist
                                for check in self.rooms.keys():
                                    print("Scanning room_list")
                                    if check == text[1]:
                                        flag = True
                                        connection.send(bytes("Error -- room already exists", "utf8"))
                                # Room doesn't exist, create it
                                if flag == False:
                                    print("Created a new room")
                                    self.rooms[text[1]] = []
                                    connection.send(bytes("You successfully created a new room!", "utf8"))
                            else:
                                    connection.send(bytes("Error -- must list at least one room", "utf8"))


                        # Send a list of usernames
                        elif text[0] == "/users" and len(text) == 1:
                            for to_print in self.users.keys():
                                connection.send(bytes(to_print, "utf8"))

                        # Send a list of usernames in a room
                        elif text[0] == "/users" and len(text) == 2:
                            for room_name, room_list in self.rooms.items():
                                if room_name == text[1]:
                                    for to_send in room_list:
                                        connection.send(bytes(to_send, "utf8"))

                        # List all rooms
                        elif text[0] == "/list":
                            for to_send in self.rooms.keys():
                                connection.send(bytes(to_send, "utf8"))
                        
                        
                        # Disconnect a user from a room
                        elif text[0] == "/disconnect":
                            print("Command: " + username + " has disconnected")
                            connection.send(bytes("--disconnect--", "utf8"))   
                            self.user_count -= 1
                            # Delete all instances of the user in each room
                            for room_name, room_check in self.rooms.items(): # Check each room for it's userlist
                                for user_check in room_check: # Check each userlist
                                    if user_check == username: # If username is in the list of users
                                        room_check.remove(user_check)
                                        print("Successfully removed user from: " + room_name)
                            # Clean up data
                            del self.users[username]
                            print("Successfully deleted user")
                            connected = False
                            connection.close()
                            print("Successfully closed connection")
                            # Close thread
                            return

                        # Send a message to a room
                        elif text[0] == '/s' and len(text) > 2:
                            # Parse the message from left to right until it doesn't match a room name
                            print(username + " may want to send to multiple rooms, doing a parse")
                            parse = text[1::]
                            rooms_to_send = []
                            end_flag = False

                            # Scan through the list of rooms the user typed until one item doesn't match
                            for check in parse:
                                for room_name, room_check in self.rooms.items():
                                    if check == room_name:
                                        print("Adding to rooms_to_send: " + check)
                                        rooms_to_send.append(room_name)
                                        end_flag = True
                                        break
                                # Verify that at least one of the rooms found matches the user's input
                                if end_flag == True:
                                    end_flag = False
                                # If no match was found, that means you found the end of the listed rooms
                                else:
                                    break
                                print("Back to check in parse loop")
                            
                            # Remove the multiple rooms listed by the user so it doesn't send each room name out
                            print(parse)
                            print("Preparing to remove all found rooms from the parse")
                            for to_remove in rooms_to_send:
                                parse.remove(to_remove)
                            
                            # Join the parse data back into a single string to echo to each user in rooms_to_send
                            print(parse)
                            print(username + " is messaging multiple rooms room")
                            each_message = " "
                            each_message = each_message.join(parse)
                            print("Parse, ready to send as each_message: " + each_message)

                            # Loop through each room
                            for room_name, room_check in self.rooms.items():
                                # Check each room listed by the user to send to
                                for check in rooms_to_send:
                                    if check == room_name:
                                        # Send the message to each user in the room
                                        for user_check in room_check:
                                            self.users[user_check].send(bytes("(" + room_name + ") " + username + ": " + each_message, "utf8"))
                                        # Successfully found a room to send to, remove it so it isn't rechecked in the main loop
                                        print("Successfully removed: " + check)
                                        rooms_to_send.remove(check)

                        # Send a private message to a user
                        elif text[0] == '/w' and len(text) > 2:
                            print(username + " is messaging a specific user")
                            # Verify user exists, if user have been found join all non-command text and send the message
                            for user_key, user_value in self.users.items():
                                if text[1] == user_key:
                                    each_message = " "
                                    each_message = each_message.join(text[2::])
                                    self.users[user_key].send(bytes("(Private To: " + user_key + ") " + username + ": " + each_message, "utf8"))
                            
                        # No valid command was sent, error
                        else:
                            # Echo to verify functionality
                            print(data)
                            connection.send(bytes("Invalid Command", "utf8"))

                    # Send a normal message
                    else:
                        print("Echoing")
                        # Check each room for it's userlist
                        for room_name, room_check in self.rooms.items(): 
                            # Check each userlist in each room
                            for user_check in room_check: 
                                # Check if username is in the list of users
                                if user_check == username: 
                                    print("User matching: " + user_check)
                                    # Send the message to all users who share a room with the sending user
                                    for shared_users in room_check:
                                        print("Shared Users: " + shared_users)
                                        print(self.users.keys())
                                        print(self.users[shared_users])
                                        self.users[shared_users].send(bytes("(" + room_name + ") " + username + ": " + scrub_data, "utf8"))
                                        
                        
            # Client disconnects with a specified username
            except:
                print(username + " has disconnected")
                # Delete all instances of the user in each room
                for room_name, room_check in self.rooms.items(): # Check each room for it's userlist
                    for user_check in room_check: # Check each userlist
                        if user_check == username: # If username is in the list of users
                            room_check.remove(user_check)
                # Clean up connection
                del self.users[username]
                self.user_count -= 1
                connection.close()

        # Client disconnects without specifying a username
        except:
            print("A user has disconnected")

    # Main Loop to maintain a connection between a server and client
    def main_loop(self):
        online = True
        print("The server is listening for a new connection (main_loop has a listener)")
        self.server.listen(5)
        while online:
            connection, address = self.server.accept()
            _thread.start_new_thread(self.connect, (connection,))
            print("A connection has been found (main_loop will create a new thread)")
        self.server.close()