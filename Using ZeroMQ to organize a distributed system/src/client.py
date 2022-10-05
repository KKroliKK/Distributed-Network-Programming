import zmq
import sys

try:
    send_port = sys.argv[1]
    receive_port = sys.argv[2]

    context = zmq.Context()

    send_sock = context.socket(zmq.REQ)
    send_sock.connect(f'tcp://localhost:{send_port}')

    receive_sock = context.socket(zmq.SUB)
    receive_sock.connect(f'tcp://localhost:{receive_port}')
    receive_sock.setsockopt_string(zmq.SUBSCRIBE, '')
    receive_sock.RCVTIMEO = 100
except:
    print('To launch the script use the following command:')
    print('python client.py 5555 5556')
    sys.exit(0)


try:
    while True:
        message = input("> ")
        if len(message) != 0:
            send_sock.send_string(f'{message}')
            send_sock.recv_string()
        try:
            while True:
                string = receive_sock.recv_string()
                print(f'{string}')
        except zmq.Again:
            pass
except KeyboardInterrupt:
    print('\nKeyboard interrupt. Shutting down.')
    sys.exit(0)