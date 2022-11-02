import grpc
import chord_pb2_grpc as pb2_grpc
import chord_pb2 as pb2
from concurrent import futures
import sys
import random

random.seed(0)


# a dictionary of id and address port pairs of all registered nodes
registry = {}
m = None
ring_size = None

class RegistryServicer(pb2_grpc.RegistryServicer):

    def get_ack(self, request, context):
        reply = pb2.ServerType(type='Registry') 
        return reply


    def get_chord_info(self, request, context):
        table = []
        for id, portaddr in registry.items():
            table.append({'id': id, 'address': portaddr})

        reply = {'table': table}
        return pb2.FingerTable(**reply)


    def deregister(self, request, context):
        id = request.id
        if id not in registry:
            reply = {
                'status': False,
                'id_message': f'id {id} is not found at the ring.'
            }
        else:
            del registry[id]
            reply = {
                'status': True,
                'id_message': f'id {id} is removed from the ring.'
            }

        return pb2.BoolReply(**reply)


    def register(self, request, context):
        if len(registry) == ring_size:
            return pb2.IdReply(
                id=-1,
                m_message=f"Registring for {request.address} is unsuccessful: Chord is full."
            )

        else:
            while True:
                id = random.randint(0, 2 ** m - 1)
                if id not in registry.keys():
                    break

            registry[id] = f"{request.address}"

            return pb2.IdReply(
                id=id,
                m_message=str(m)
            )


    def populate_finger_table(self, request, context):
        id = request.id

        def fingers_generator(id):
            for power in range(m):
                yield (id + 2 ** power) % ring_size

        def find(finger):
            for i in range(ring_size):
                node = (finger + i) % ring_size
                if node in registry.keys():
                    return node

        def find_predecessor(id):
            for i in range(1, ring_size + 1):
                node = (id - i + ring_size) % ring_size
                if node in registry.keys():
                    return node

        fingers = set()

        for finger in fingers_generator(id):
            node = find(finger)
            fingers.add(node)

        table = []
        for key, portaddr in registry.items():
            if key in fingers:
                table.append({'id': key, 'address': portaddr})

        predecessor_id = find_predecessor(id)

        pred = pb2.NodeInfo(
            id=predecessor_id
        )

        table = pb2.FingerTable(table=table)

        reply = pb2.PopFingTableRep(
            predecessor=pred, 
            table=table
        )

        return reply


address = sys.argv[1]
m = int(sys.argv[2])
ring_size = 2 ** m

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
pb2_grpc.add_RegistryServicer_to_server(RegistryServicer(), server)

print(f'Starting Registry. Listening on address {address}. "m" is equal to {m}')
server.add_insecure_port(address)


server.start()
try:
    server.wait_for_termination()
except KeyboardInterrupt:
    print('\nKeyboard interrupt. Shutting down')
