import grpc
import chord_pb2 as pb2
import chord_pb2_grpc
import sys


stub = None
server_type = None
node_id = None


try:
    while True:
        user_input = input('\n> ')
        command, *data = user_input.split()


        if command == 'connect':
            address = data[0]
            channel = grpc.insecure_channel(address)
            message = pb2.Empty()

            try:
                stub = chord_pb2_grpc.RegistryStub(channel)
                response = stub.get_ack(message)

            except grpc._channel._InactiveRpcError:
                stub = chord_pb2_grpc.NodeStub(channel)
                response = stub.get_ack(message)

            server_type = response.type
            node_id = response.id
            print('Connected to', server_type)

        elif command == 'get_info':
            if server_type == 'Registry':
                response = stub.get_chord_info(pb2.Empty())

            elif server_type == 'Node':
                print('Node id:', node_id)
                print('Finger Table:')
                response = stub.get_finger_table(pb2.Empty())

            for node in response.table:
                print('{:2d}:    {}'.format(node.id, node.address))

        elif command == 'save':
            message = {
                'key': data[0][1:-1],
                'text': ' '.join(data[1:])
            }
            message = pb2.Data(**message)
            response = stub.save(message)
            print(f'{response.status}, {response.id_message}')

        elif command == 'remove':
            message = {
                'key': data[0]
            }
            message = pb2.Key(**message)
            response = stub.remove(message)
            print(f'{response.status}, {response.id_message}')


        elif command == 'find':
            message = {
                'key': data[0]
            }
            message = pb2.Key(**message)
            response = stub.find(message)
            print(f'{response.status}, {response.id_message}')


        elif command == 'quit':
            print('Goodbye!')
            sys.exit(0)


        else:
            print('invalid command')
        
        
except KeyboardInterrupt:
    print('\nKeyboard interrupt. Shutting down.')
    sys.exit(0)