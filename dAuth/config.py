# This file contains global configuration objects
# Default values should be set here
# In the main file, an instance of each of these should be made 
#  and given to the respective service
# Values can be changed at runtime via parser/input (TODO)


# Used for anything not tied to a particular manager
class CCellularConfig:
    # Randomly generate id in ccellular init
    ID = None
    OUTPUT_DIR = "./output"


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

