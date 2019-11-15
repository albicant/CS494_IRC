# Server Implementation
# Implementation of the main server function
# Michael Long, Gennadii Sytov
# CS494 Final Project, June 2019

import CS494_Server_Handler as server

def main():
    
    print('Michael Long, Gennadii Sytov -- CS494: Server')
   
    # Distinguish whether to launch the server locally or online
    t_host = '127.0.0.1'
    t_port = 1234
    flag = True
    # Loop input until the Server successfully launches
    while flag:
        try:
            print("Please specify an IP to launch the server on (localhost is 127.0.0.1)")
            t_host = input()
            print("Please specify a Port to connect to (default is 1234)")
            t_port = input()
            t_port = int(t_port)
            # Launch the server
            server_app = server.server_handler(host = t_host, port = t_port)
            flag = False
            server_app.main_loop()
        except:
            print("Error, either Server is launched with specified IP or invalid IP or Port value")

if __name__ == '__main__':
    main()


