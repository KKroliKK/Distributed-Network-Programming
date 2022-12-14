import grpc
import raft_pb2 as pb2
import raft_pb2_grpc as pb2_grpc
import sys


stub = None
print('The client starts')


def get_stub(address):
    channel = grpc.insecure_channel(address)
    stub = pb2_grpc.RaftStub(channel)
    return stub


try:
    while True:
        user_input = input('\n> ')
        command, *data = user_input.split()

        if command == 'connect':
            ip_addr = data[0]
            port = data[1]
            address = f'{ip_addr}:{port}'

            stub = get_stub(address)

        elif command == 'getleader':
            try:
                message = pb2.Empty()
                response = stub.get_leader(message)
                print(response.id, response.address)
            except grpc._channel._InactiveRpcError:
                print('Server is not available now. Try later.')

        elif command == 'suspend':
            try:
                period = float(data[0])
                message = pb2.Period(period=period)
                response = stub.suspend(message)
            except grpc._channel._InactiveRpcError:
                print('Server is not available now. Try later.')

        elif command == 'quit':
            print('The client ends')
            sys.exit(0)


        else:
            print('invalid command')
        

except KeyboardInterrupt:
    print('\nKeyboard interrupt. Client is shutting down.')
    sys.exit(0)