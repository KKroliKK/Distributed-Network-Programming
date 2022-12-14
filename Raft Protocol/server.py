import grpc
from concurrent import futures
import raft_pb2 as pb2
import raft_pb2_grpc as pb2_grpc
import sys
from time import sleep
import random
from threading import Timer
from threading import Thread
from enum import Enum
from threading import Lock
import functools


class State(Enum):
    follower = 1
    candidate = 2
    leader = 3


def read_config():
    '''Returns config dict in format:
    {0: '127.0.0.1:50000',
     1: '127.0.0.1:50001',
     2: '127.0.0.1:50002'}
    '''
    addresses = {}

    with open('Config.conf') as file:
        text = file.read()

    lines = text.splitlines()
    for line in lines:
        line = line.split()

        id = int(line[0])
        ip_addr = line[1]
        port = line[2]

        addresses[id] = ip_addr + ':' + port

    return addresses


class RaftServer(pb2_grpc.RaftServicer):
    def __init__(self, id: int, addresses: dict):
        self.id = id
        self.addresses = addresses
        self.term = 0
        self.suspended = False

        self.start_server()
        self.become_follower()
        self.heartbeat_timeout = 0.05
        self.leader_id = None
        self.voted_for = None
        self.stubs = self.get_voters_stubs()

        self.last_hb = -1


    def generate_timeout(self):
        timeout = random.uniform(0.5, 0.7)
        return timeout


    def start_server(self, delay=0):
        sleep(delay)

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=30))
        pb2_grpc.add_RaftServicer_to_server(self, server)

        address = addresses[self.id]
        server.add_insecure_port(address)

        server.start()
        self.server = server


    def suspend(self, request, context):
        period = request.period
        print(f'Command from client: suspend {period}')
        print(f'Sleeping for {period} seconds.')

        self.suspended = True
        sleep(period)
        self.suspended = False
        
        return pb2.Empty()


    def suspend_decorator(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.suspended:
                return pb2.Empty()

            return func(self, *args, **kwargs)

        return wrapped


    @suspend_decorator
    def become_follower(self):
        self.state = State.follower
        self.reset_leader_timer(stop=True)
        self.timeout = self.generate_timeout()
        print('I am a follower. Term:', self.term)
        self.reset_timer()


    @suspend_decorator
    def ask_for_vote(self, stub):
        request = pb2.Vote(term=self.term, candidate_id=self.id)
        try:
            response = stub.request_vote(request)
            if response.term > self.term:
                self.check_term(response.term)
                return
            lock = Lock()
            lock.acquire()
            self.num_votes += response.vote
            self.num_nodes += 1
            lock.release()
        except grpc._channel._InactiveRpcError:
            pass


    @suspend_decorator
    def become_candidate(self):
        print('The leader is dead')
        self.state = State.candidate
        self.term += 1
        print('I am a candidate. Term:', self.term)

        self.voted_for = self.id
        print('Voted for node', self.voted_for)
        self.num_votes = 1
        self.num_nodes = 1

        self.stubs = self.get_voters_stubs()
        threads = [Thread(target=self.ask_for_vote, args=(stub,)) for stub in self.stubs]
        [t.start() for t in threads]
        [t.join() for t in threads]
            
        print('Votes received')

        if self.check_number_of_votes():
            self.become_leader()
        else:
            self.become_follower()


        
    @suspend_decorator
    def check_number_of_votes(self):
        
        if self.num_votes > (self.num_nodes // 2):
            return True
        else:
            return False


    @suspend_decorator
    def become_leader(self):
        self.reset_timer(stop=True)
        self.state = State.leader
        self.leader_id = self.id
        print('I am a leader. Term:', self.term)
        self.reset_leader_timer()


    @suspend_decorator
    def reset_timer(self, stop=False):
        if self.state != State.leader:
            try:
                self.timer.cancel()
            except AttributeError:  
                pass    # in case it's the first timer
            if stop == False:
                self.timer = Timer(self.timeout, self.become_candidate)
                self.timer.start()


    @suspend_decorator
    def reset_leader_timer(self, stop=False):
        try:
            self.leader_timer.cancel()
        except AttributeError:  
            pass    # in case it's the first timer
        
        if stop == False:
            self.leader_timer = Timer(self.heartbeat_timeout, self.send_appends)
            self.leader_timer.start()


    @suspend_decorator
    def get_voters_stubs(self):
        stubs = []

        for id, address in self.addresses.items():    
            if id == self.id:
                continue
            channel = grpc.insecure_channel(address)
            stub = pb2_grpc.RaftStub(channel)
            stubs.append(stub)

        return stubs

    
    @suspend_decorator
    def check_term(self, term):
        if self.term < term:
            self.term = term
            self.voted_for = None
            self.leader_id = None
            self.become_follower()


    @suspend_decorator
    def request_vote(self, request, context):
        if self.state == State.follower:
            self.reset_timer() 
        self.check_term(request.term)
        
        if self.voted_for == None and self.term == request.term:
            vote = True
            self.voted_for = request.candidate_id
            self.leader_id = self.voted_for
            print('Voted for node', self.voted_for)
        else:
            vote = False
        
        return pb2.Bulletin(term=self.term, vote=vote)


    @suspend_decorator
    def send_append(self, stub):
        req = pb2.Systole(term=self.term, leader_id=self.id)
        try:
            response = stub.append_entries(req)
            if response.success == False:
                self.check_term(response.term)
                return
        except grpc._channel._InactiveRpcError:
            pass


    @suspend_decorator
    def send_appends(self):
        self.stubs = self.get_voters_stubs()
        threads = [Thread(target=self.send_append, args=(stub,)) for stub in self.stubs]
        [t.start() for t in threads]
        [t.join() for t in threads]

        if self.state == State.leader:
            self.reset_leader_timer()


    @suspend_decorator
    def append_entries(self, request, context):
        if self.state == State.follower:
            self.reset_timer() 
        success = False

        if request.term >= self.term:
            success = True
            if self.leader_id == None and self.voted_for == None:
                self.voted_for = self.leader_id
            self.leader_id = request.leader_id
        self.check_term(request.term)

        self.last_hb = request.leader_id

        return pb2.Diastole(term=self.term, success=success)


    @suspend_decorator
    def get_leader(self, request, context):
        print('Command from client: getleader')
        if self.leader_id == None:
            if self.voted_for == None:
                id = None
                address = None
            else:
                id = self.voted_for
                address = self.addresses[self.voted_for]
        else:
            id = self.leader_id
            address = self.addresses[self.leader_id]

        print(id, address)

        return pb2.ServerInfo(id=id, address=address)


id = int(sys.argv[1])
addresses = read_config()
address = addresses[id]

server = RaftServer(id, addresses)

print('Server is started at', address)

try:
    server.server.wait_for_termination()
    
except KeyboardInterrupt:
    print('\nKeyboard interrupt. Shutting down')