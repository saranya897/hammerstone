import hammerstone_pb2
import hammerstone_pb2_grpc
from utils import Utils


class GreeterService(hammerstone_pb2_grpc.GreeterService):
    
    def __init__(self):
        self.utils = Utils()

    def SayHello(self, request, context):
        print(request.name)
        return hammerstone_pb2.HelloReply(message='Hello, %s!' % request.name)
