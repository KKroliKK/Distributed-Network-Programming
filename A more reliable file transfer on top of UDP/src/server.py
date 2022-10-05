'''
    Lab 1: reliable file transfer on top of UDP
	Author: Andrey Vagin
    Email: a.vagin@innopolis.university
    Group: B20-AI
'''

import socket
import sys
import time

HOST = 'localhost'
PORT = 8888
BUFFER_SIZE = 1024
TIMEOUT = 0.5


def server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Bind socket to local host and port
        try:
            s.bind((HOST, PORT))
            s.settimeout(TIMEOUT)
        except socket.error as msg:
            print(f'Bind failed: {msg}')
            sys.exit()
	
        print('Socket bind complete')
        
        sessions = {}
        #now keep talking with the client
        while True:
            # check finished sessions
            for host in list(sessions.keys()):
                file = sessions[host]['file']
                filename = sessions[host]['filename']
                size = sessions[host]['size']
                last_active = sessions[host]['last_active']
                if len(file) == size and time.time() - last_active >= 1:
                    info = sessions.pop(host)
                    # save file
                    # path = './server/' + f'{filename}'
                    path = f'{filename}'
                    with open(path, 'wb+') as output:
                        output.write(file)
                    print(f"Successfully finished session with the host {host} (1 second timeout).")


            # check whether the client is active for three seconds
            for host in list(sessions.keys()):
                last_active = sessions[host]['last_active']
                if time.time() - last_active >= 3:
                    sessions.pop(host)
                    print(f"The host {host} is inactive for 3 seconds, session termination")


            # receive data from client (data, addr)
            try:
                message, addr = s.recvfrom(BUFFER_SIZE)
                message_type = message[:1].decode()
            except:
                continue
            
            if message_type == 's':
                message = message.decode()
                desc, seqno, filename, total_size = message.split(' | ')
                reply = f'a | {int(seqno) + 1} | {BUFFER_SIZE}'
                s.sendto(reply.encode(), addr)

                sessions[addr[1]] = {
                    'filename': filename,
                    'seqno': int(seqno) + 1,
                    'size': int(total_size),
                    'last_active': time.time(),
                    'file': b''
                }

            if message_type == 'd':
                # Let's find indexes of | separators
                # | symbol has value of 124
                first_sep = list(message).index(124)
                second_sep = list(message).index(124, first_sep + 1)

                sessions[addr[1]]['last_active'] = time.time()
                seqno = int(message[first_sep + 1: second_sep])
                data = message[second_sep + 2:]
                if seqno == sessions[addr[1]]['seqno']:
                    sessions[addr[1]]['seqno'] = seqno + 1
                    sessions[addr[1]]['file'] += data

                    ack_message = f'a | {seqno + 1}'
                    s.sendto(ack_message.encode(), addr)
                    
            
	


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("To launch the program use:\n\n python server.py port")
        sys.exit()

    PORT = int(sys.argv[1])
    server()


# kill -9 $(lsof -t -i udp:8888)
# ./good_client 127.0.0.1:8888 redpanda.jpg redpanda_good.jpg
# ./bad_client 127.0.0.1:8888 redpanda.jpg redpanda_bad.jpg