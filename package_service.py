import configparser
from pymongo import MongoClient
import hammerstone_pb2
import hammerstone_pb2_grpc
import

class PackageService(hammerstone_pb2_grpc.PackageService):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(".env")

       
    
