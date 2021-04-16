import grpc
from concurrent import futures
import time
import hammerstone_pb2
import hammerstone_pb2_grpc
import configparser
import sys
from greeter_service import GreeterService
from profile_service import ProfileService


def serve():
    config = configparser.ConfigParser()   # to read .env file
    config.read('.env')

    workers = config['grpc']['workers']

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=int(workers)))

    # adding services
    hammerstone_pb2_grpc.add_GreeterServiceServicer_to_server(
        GreeterService(), server)
    hammerstone_pb2_grpc.add_ProfileServiceServicer_to_server(
        ProfileService(), server)

    server.add_insecure_port('[::]:50053')
    print('Starting insecure server on port 50051...')

    try:
        server.start()
        server.wait_for_termination()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    try:
        serve()
    except Exception as e:
        print(e)
