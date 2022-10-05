import zmq
import sys
import math


try:
    receive_port = sys.argv[1]
    send_port = sys.argv[2]

    context = zmq.Context()

    send_sock = context.socket(zmq.PUB)
    send_sock.connect(f'tcp://localhost:{send_port}')

    receive_sock = context.socket(zmq.SUB)
    receive_sock.connect(f'tcp://localhost:{receive_port}')
    receive_sock.setsockopt_string(zmq.SUBSCRIBE, 'gcd')
    receive_sock.RCVTIMEO = 100
except:
    print('To launch the script use the following command:')
    print('python gcd.py 5557 5558')
    sys.exit(0)


try:
    while True:
        try:
            while True:
                string = receive_sock.recv_string()
                text, a, b = string.split()
                a, b = int(a), int(b)
                gcd = math.gcd(a, b)
                send_sock.send_string(f'gcd for {a} {b} is {gcd}')
                
        except zmq.Again:
            pass
except KeyboardInterrupt:
    print('\nKeyboard interrupt. Shutting down.')
    sys.exit(0)