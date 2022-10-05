from webbrowser import Elinks
import grpc
import service_pb2
import service_pb2_grpc
import sys


addres = sys.argv[1]
channel = grpc.insecure_channel(addres)
stub = service_pb2_grpc.CommandExecutorStub(channel)


try:
    while True:
        message = input("> ")
        command, *data = message.split(maxsplit=1)

        if command == 'reverse':
            text = service_pb2.TextRev(text=data[0])
            response = stub.ReverseText(text)
            print(response)

        elif command == 'split':
            text = service_pb2.TextSplitReq(text=data[0], delim=' ')
            response = stub.SplitText(text)
            print(response)

        elif command == 'isprime':
            numbers = data[0].split()
            numbers = [int(number) for number in numbers]

            for number in numbers:
                req = service_pb2.Number(value=number)
                response = stub.IsPrime(req)

                if response.value == True:
                    print(number, 'is prime')
                else:
                    print(number, 'is not prime')

        elif command == 'exit':
            print('Goodbye!')
            sys.exit(0)

        else:
            print('invalid command')
        
        
except KeyboardInterrupt:
    print('\nKeyboard interrupt. Shutting down.')
    sys.exit(0)