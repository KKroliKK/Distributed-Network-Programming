'''
    Lab 2: Multithreaded client-server socket programming
	Author: Andrey Vagin
    Email: a.vagin@innopolis.university
    Group: B20-AI
'''

from queue import Empty
from socket import socket, AF_INET, SOCK_STREAM, timeout
from multiprocessing import Queue
from threading import Thread
import sys

IP_ADDR = '127.0.0.1'
if len(sys.argv) == 2:
    PORT = int(sys.argv[1])
else:
    PORT = 65432
BUF_SIZE = 16
NUM_WORKERS = 2
stop_threads = False


def is_prime(n):
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for divisor in range(3, n, 2):
        if n % divisor == 0:
            return False
    return True


def reply_to_client(number: str):
    number = int(number)
    if is_prime(number):
        return f'{number} is prime'.encode()
    else:
        return f'{number} is not prime'.encode()


def serve_client(q: Queue):
    while True:
        if stop_threads == True:
            break
        try:
            conn, addr = q.get(block=True, timeout=0.01)
            print(f'{addr} connected')
            while True:
                number = conn.recv(BUF_SIZE)
                if number:
                    print(f'Received number: {number.decode()} from {addr}')
                    reply = reply_to_client(number)
                    conn.send(reply)
                else:
                    print(f'{addr} disconnected')
                    break
        except Empty:
            pass


with socket(AF_INET, SOCK_STREAM) as s:
    s.bind((IP_ADDR, PORT))
    s.listen()
    s.settimeout(5)
    try:
        q = Queue()
        threads = [Thread(target=serve_client, args=(q,)) for _ in range(NUM_WORKERS)]
        [t.start() for t in threads]
        while True:
            try:
                print('Waiting for a new connection')
                q.put(s.accept())
            except timeout:
                print('No connection request')
            except Exception as e:
                print(e)
                break
    except KeyboardInterrupt:
        stop_threads = True
        [t.join() for t in threads]
        print('Terminated by keyboard interrupt')
    print('Server is shutting down.')