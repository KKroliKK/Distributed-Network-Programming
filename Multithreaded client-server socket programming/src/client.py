'''
    Lab 2: Multithreaded client-server socket programming
	Author: Andrey Vagin
    Email: a.vagin@innopolis.university
    Group: B20-AI
'''

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import sys

if len(sys.argv) == 2:
    address = sys.argv[1].split(":")
    DEST_IP_ADDR, DEST_PORT = (address[0], int(address[1]))
else:
    DEST_IP_ADDR = '127.0.0.1'
    DEST_PORT = 65432
BUF_SIZE = 1024
NUM_WORKERS = 1


numbers = [15492781, 15492787, 15492803,
           15492811, 15492810, 15492833,
           15492859, 15502547, 15520301,
           15527509, 15522343, 1550784]

def client(idx):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((DEST_IP_ADDR, DEST_PORT))
        print(f'Connected to (DEST_IP_ADDR, DEST_PORT)')

        for number in numbers:
            s.send(str(number).encode())
            print(f'Sent number: {number}')
            response = s.recv(BUF_SIZE)
            print(f'Received message: {response.decode()}')

        print(f'Client {idx} completed')


[Thread(target=client, args=(idx,)).start() for idx in range(NUM_WORKERS)]