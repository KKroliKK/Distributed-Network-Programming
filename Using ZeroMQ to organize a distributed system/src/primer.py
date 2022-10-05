import zmq
import sys


def isprime(n):
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n < 2:
        return False
    for i in range(3, int(n**0.5)+1, 2):
        if n % i == 0:
            return False

    return True


try:
    receive_port = sys.argv[1]
    send_port = sys.argv[2]

    context = zmq.Context()

    send_sock = context.socket(zmq.PUB)
    send_sock.connect(f'tcp://localhost:{send_port}')

    receive_sock = context.socket(zmq.SUB)
    receive_sock.connect(f'tcp://localhost:{receive_port}')
    receive_sock.setsockopt_string(zmq.SUBSCRIBE, 'isprime')
    receive_sock.RCVTIMEO = 100
except:
    print('To launch the script use the following command:')
    print('python primer.py 5557 5558')
    sys.exit(0)


try:
    while True:
        try:
            while True:
                string = receive_sock.recv_string()
                string = string.split()
                number = int(string[1])

                if isprime(number) == True:
                    send_sock.send_string(f'{number} is prime')
                else:
                    send_sock.send_string(f'{number} is not prime')
                    
        except zmq.Again:
            pass
except KeyboardInterrupt:
    print('\nKeyboard interrupt. Shutting down.')
    sys.exit(0)