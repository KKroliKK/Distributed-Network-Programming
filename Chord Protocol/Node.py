import grpc
from concurrent import futures
import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
import sys
import time
import zlib


registry_stub = None
id = None
ipaddr_port = None
m = None
ring_size = None
predecessor_id = None
successor_id = None
finger_table = {}
storage = {}    # {key: value}, node id to store = hash(key)


class NodeHandler(pb2_grpc.NodeServicer):

    def get_ack(self, request, context):
        reply = pb2.ServerType(type='Node', id=id)
        return reply


    def get_finger_table(self, request, context):
        ft = []
        for node_id, node_port in finger_table.items():
            ft.append(pb2.NodeInfo(id=node_id, address=node_port))

        return pb2.FingerTable(table=ft)


    def save(self, request, context):
        get_finger_table()
        key, text = request.key, request.text
        target_id = get_target_id(key)
        
        if target_id in get_stored_indexes(predecessor_id, id):
            if key not in storage:
                storage[key] = text
                return pb2.BoolReply(
                    status=True,
                    id_message= f'Text "{text}" is saved with key "{key}" to node {id}'
                )
            else:
                return pb2.BoolReply(
                    status=False,
                    id_message= f'Failed to save: the key "{key}" is already presented at node {id}.'
                )
        
        elif target_id in get_stored_indexes(id, successor_id):
            successor_address = finger_table[successor_id]
            stub = get_node_stub(successor_address)
            return stub.save(request)

        else:
            node_id = find_node_to_forward(target_id)
            node_address = finger_table[node_id]
            stub = get_node_stub(node_address)
            return stub.save(request)

    def save_to_pred(self, request, context):
        predecessor_address, ids = request.predecessor_address, request.required_ids
        predecessor_stub = get_node_stub(predecessor_address)
        
        for key, text in storage.items():
            if get_target_id(key) in ids:
                save_req = pb2.Data(key=key, text=text)
                save_rep = predecessor_stub.save(save_req)

        return pb2.Empty()


    def find(self, request, context):
        get_finger_table()
        key = request.key
        target_id = get_target_id(key)
        
        if target_id in get_stored_indexes(predecessor_id, id):
            if key not in storage:
                return pb2.BoolReply(
                    status=False,
                    id_message= f'{key} does not exist in node {id}'
                )
            else:
                return pb2.BoolReply(
                    status=True,
                    id_message= f'{key} is saved in node {id}.'
                )
        
        elif target_id in get_stored_indexes(id, successor_id):
            successor_address = finger_table[successor_id]
            stub = get_node_stub(successor_address)
            return stub.find(request)

        else:
            node_id = find_node_to_forward(target_id)
            node_address = finger_table[node_id]
            stub = get_node_stub(node_address)
            return stub.find(request)


    def remove(self, request, context):
        get_finger_table()
        key = request.key
        target_id = get_target_id(key)
        
        if target_id in get_stored_indexes(predecessor_id, id):
            if key not in storage:
                return pb2.BoolReply(
                    status=False,
                    id_message= f'{key} does not exist in node {id}'
                )
            else:
                del storage[key]
                return pb2.BoolReply(
                    status=True,
                    id_message= f'{key} is removed from node {id}.'
                )
        
        elif target_id in get_stored_indexes(id, successor_id):
            successor_address = finger_table[successor_id]
            stub = get_node_stub(successor_address)
            return stub.remove(request)

        else:
            node_id = find_node_to_forward(target_id)
            node_address = finger_table[node_id]
            stub = get_node_stub(node_address)
            return stub.remove(request)


    def get_finger_table_loop(self):
        while True:
            get_finger_table()
            time.sleep(1)


    def __init__(self) -> None:
        super().__init__()

        register_node()
        get_finger_table()


def get_target_id(key):
    hash_value = zlib.adler32(key.encode())
    id = hash_value % ring_size
    return id


def get_stored_indexes(pred_id, node_id):
    size = node_id - pred_id
    if size <= 0:
        size += ring_size
    stored_indexes = [(i + pred_id) % ring_size for i in range (1, size + 1)]
    return stored_indexes


def find_node_to_forward(target_id):
    target_id = target_id if target_id > id else target_id + ring_size
    ft = sorted([node_id if node_id > id else node_id + ring_size for node_id in finger_table.keys()])
    ft.append(id + ring_size)
    
    for idx in range(0, len(ft) - 1):
        if ft[idx] <= target_id and ft[idx + 1] > target_id:
            node_id = ft[idx] % ring_size
            return node_id


def register_node():
    global id
    global m
    global ring_size

    message = pb2.Address(address=ipaddr_port)
    reply = registry_stub.register(message)

    try:
        id = reply.id
        m = int(reply.m_message)
        ring_size = 2 ** m
    except ValueError:
        print(reply.m_message)
        sys.exit()


def get_finger_table():
    global predecessor_id
    global successor_id
    global finger_table

    messsage = pb2.Id(id=id)
    reply = registry_stub.populate_finger_table(messsage)

    reply_finger_table = reply.table.table
    finger_table = {}
    for node_info in reply_finger_table:
        finger_table[node_info.id] = node_info.address

    predecessor_id = reply.predecessor.id
    successor_id = find_succecessor()


def find_succecessor():
    for i in range(1, ring_size + 1):
        node = (id + i + ring_size) % ring_size
        if node in finger_table:
            return node


def quit():
    print(f"\nShutting down node {id} ...")

    # deregister the node
    deregister_req = pb2.Id(id=id)
    deregister_rep = registry_stub.deregister(deregister_req)

    successor_stub = get_node_stub(finger_table[successor_id])
    # transfer all data in its storage to its successor
    for key, text in storage.items():
        save_at_id_req = pb2.Data(key=key, text=text)
        save_at_id_rep = successor_stub.save(save_at_id_req)

    sys.exit(0)


def get_node_stub(ipaddr_port):
    channel = grpc.insecure_channel(ipaddr_port)
    stub = pb2_grpc.NodeStub(channel)
    return stub

    
def request_ids_from_successor():
    required_ids = get_stored_indexes(predecessor_id, id)
    successor_stub = get_node_stub(finger_table[successor_id])
    save_to_pred_req = pb2.Ids(predecessor_address=ipaddr_port, required_ids=required_ids)
    save_to_pred_rep = successor_stub.save_to_pred(save_to_pred_req)


if __name__ == '__main__':
    try:
        channel = grpc.insecure_channel(sys.argv[1])
        registry_stub = pb2_grpc.RegistryStub(channel)

        ipaddr_port = sys.argv[2]

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        node_handler = NodeHandler()
        pb2_grpc.add_NodeServicer_to_server(node_handler, server)

        print(f'Starting node {id}.')
        server.add_insecure_port(ipaddr_port)
        server.start()
        
        request_ids_from_successor()

        # populate ft every second
        node_handler.get_finger_table_loop()

        server.wait_for_termination()

    except KeyboardInterrupt:
        quit()