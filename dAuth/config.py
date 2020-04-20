# This file contains global configuration objects
# Default values should be set here


class NetworkManagerConfig:
    # General
    GRPC_PORT = 13127
    OUTPUT_DIR = "./output"
    PRIORITIES = [0,1,2]
    LIMIT_PRIORITIES = True
    
    # Logging
    LOGGING_SERVER_HOST = "localhost"
    LOGGING_SERVER_PORT = 14127


class DatabaseManagerConfig:
    pass


class DistributedManagerConfig:
    pass

