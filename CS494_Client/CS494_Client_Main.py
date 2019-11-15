# Client Implementation
# Implementation of the main client function
# Michael Long, Gennadii Sytov
# CS494 Final Project, June 2019

import CS494_Client_Handler as client

def main():

    # Define a default host and port for the client to connect to
    t_host = '127.0.0.1'
    t_port = 1234
    flag = True
    # Loop input until the Client successfully connects to a Server
    while flag:
        try:
            print("Please specify an IP to connect to (localhost is 127.0.0.1)")
            t_host = input()
            print("Please specify a Port to connect to (localhost is 1234)")
            t_port = input()
            t_port = int(t_port)
            user = client.client_handler(host = t_host, port = t_port)
            flag = False
            user.main_loop()
        except:
            print("Error, invalid IP or Port value")

if __name__ == '__main__':
    main()
