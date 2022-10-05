import imp
import grpc
from concurrent import futures
import service_pb2
import service_pb2_grpc
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


class CommandExecutorServicer(service_pb2_grpc.CommandExecutorServicer):
    def ReverseText(self, request, context):
        text = request.text[::-1]
        reply = {'text': text}
        return service_pb2.TextRev(**reply)

    def SplitText(self, request, context):
        text = request.text
        delim = request.delim
        splitted = text.split(delim)
        
        reply = {'number': len(splitted), 'text': splitted}
        return service_pb2.TextSplitRep(**reply)

    def IsPrime(self, request, context):
        number = request.value
        answer = isprime(number)

        reply = {'value': answer}
        return service_pb2.Answer(**reply)


server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

service_pb2_grpc.add_CommandExecutorServicer_to_server(CommandExecutorServicer(), server)

port = sys.argv[1]
print(f'Starting server. Listening on port {port}.')
server.add_insecure_port(f'[::]:{port}')

server.start()
try:
    server.wait_for_termination()
except KeyboardInterrupt:
    print('\nKeyboard interrupt. Shutting down')