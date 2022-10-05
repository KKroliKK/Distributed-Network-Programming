'''
    Lab 1: reliable file transfer on top of UDP
	Author: Andrey Vagin
    Email: a.vagin@innopolis.university
    Group: B20-AI
'''

import socket
import sys
import os

RETRIES_NUMBER = 5
TIMEOUT = 0.5
CLIENT_BUFFER_SIZE = 1024


def terminate(message):
    print(message)
    sys.exit()


def client():
    # parsing console input
    if len(sys.argv) != 4:
        terminate("To launch the program use:\n\n\
             python client.py server-hostname:port file_path filename_on_server")

    address = sys.argv[1].split(":")
    server_address = (address[0], int(address[1]))
    file_path = sys.argv[2]
    filename_on_server = sys.argv[3]
    file_size = os.path.getsize(file_path)

    # create socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(TIMEOUT)
    except socket.error:
        terminate("Socket creation error")

    # sending start message
    start_message = f"s | 0 | {filename_on_server} | {file_size}"

    attempts_counter = 0
    while attempts_counter < RETRIES_NUMBER:
        attempts_counter += 1

        s.sendto(start_message.encode(), server_address)

        try:
            response, address = s.recvfrom(CLIENT_BUFFER_SIZE)
            # parse start ack message
            parameters = response.decode().split(" | ")
            if len(parameters) != 3:
                terminate("Incorrect format of ack message")

            if parameters[0] != 'a':
                terminate("Receive not ack message")

            sequence_number = int(parameters[1])

            buffer_size = int(parameters[2])
            break
        except:
            continue

    else:
        terminate("Server is malfunctioning, terminate")


    # sending file

    with open(file_path, 'rb') as file:
        while True:
            message = f"d | {sequence_number} | ".encode()
            current_message_size = len(message)

            data = file.read(abs(buffer_size - current_message_size))
            if not data:
                terminate("Successfully transmitted a file")

            message += data

            attempts_counter = 0
            while attempts_counter < RETRIES_NUMBER:
                attempts_counter += 1

                s.sendto(message, server_address)
                try:
                    response, address = s.recvfrom(CLIENT_BUFFER_SIZE)
                    # parse ack message
                    parameters = response.decode().split(" | ")
                    if len(parameters) != 2:
                        terminate("Incorrect format of ack message")

                    if parameters[0] != 'a':
                        terminate("Receive not ack message")

                    sequence_number = int(parameters[1])

                    break
                except:
                    print(f"Retry... seqNo={sequence_number}")
                    continue
            else:
                terminate("Server is malfunctioning, terminate session")
    

    

if __name__ == '__main__':
    client()


# python client.py 127.0.0.1:8888 redpanda.jpg redpanda_a.jpg
# ./good_server 8888
# ./bad_server 8888