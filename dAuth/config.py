# This file contains global configuration objects
# Default values should be set here
# In the main file, an instance of each of these should be made 
#  and given to the respective manager
# Values can be changed at runtime via parser


# Used for anything not tied to a particular manager
class CCellularConfig:
    NAME = "CCellular"

    # Randomly generate id in ccellular init
    ID = None
    OUTPUT_DIR = "./output"

    LOGGING_ENABLED = True


class NetworkManagerConfig:
    NAME = "Network Manager"

    # General
    GRPC_PORT = 13127
    OUTPUT_DIR = "./output"
    PRIORITIES = [0,1,2]
    LIMIT_PRIORITIES = True
    
    # Logging
    LOGGING_SERVER_HOST = "localhost"
    LOGGING_SERVER_PORT = 14127


class DatabaseManagerConfig:
    NAME = "Database Manager"

    # Database
    HOST = 'localhost'
    PORT = 27017
    DATABASE_NAME = "open5gs"
    COLLECTION_NAME = "subscribers"

    # Name of distributed manager to talk to
    DISTRIBUTED_MANAGER_NAME = None


class DistributedManagerConfig:
    NAME = "Distributed Manager"

    DATABASE_MANAGER_NAME = DatabaseManagerConfig.NAME


# Hack, sorry
DatabaseManagerConfig.DISTRIBUTED_MANAGER_NAME = DistributedManagerConfig.NAME