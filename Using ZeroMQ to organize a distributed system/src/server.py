import zmq
import sys


def check_prime(string):
    try: 
        text, number = string.split()
        number = int(number)

        if text == 'isprime' and number > 0:
            return True
        else:
            return False
    except ValueError:
        return False


def check_gcd(string):
    try: 
        text, a, b = string.split()
        a, b = int(a), int(b)

        if text == 'gcd' and a > 0 and b > 0:
            return True
        else:
            return False
    except ValueError:
        return False


try:
    input_cl_port = sys.argv[1]
    out_cl_port = sys.argv[2]
    input_wr_port = sys.argv[3]
    out_wr_port = sys.argv[4]

    context = zmq.Context()

    input_cl_sock = context.socket(zmq.REP)
    input_cl_sock.bind(f'tcp://*:{input_cl_port}')
    input_cl_sock.RCVTIMEO = 100

    out_cl_sock = context.socket(zmq.PUB)
    out_cl_sock.bind(f'tcp://*:{out_cl_port}')

    out_wr_sock = context.socket(zmq.PUB)
    out_wr_sock.bind(f'tcp://*:{input_wr_port}')

    input_wr_sock = context.socket(zmq.SUB)
    input_wr_sock.bind(f'tcp://*:{out_wr_port}')
    input_wr_sock.setsockopt_string(zmq.SUBSCRIBE, '')
    input_wr_sock.RCVTIMEO = 100

except:
    print('To launch the script use the following command:')
    print('python server.py 5555 5556 5557 5558')
    sys.exit(0)
    

try:
    while True:
        try:
            message = input_cl_sock.recv_string()
            input_cl_sock.send_string('')
            out_cl_sock.send_string(message)

            if check_prime(message) == True or check_gcd(message) == True:
                out_wr_sock.send_string(message)
        except zmq.Again:
            pass

        try:
            message = input_wr_sock.recv_string()
            out_cl_sock.send_string(message)
        except zmq.Again:
            pass

except KeyboardInterrupt:
    print('\nKeyboard interrupt. Shutting down.')