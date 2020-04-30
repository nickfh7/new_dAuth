import getpass

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

    # This is the funciton to call after completing startup
    RUN_FUNCTION = None


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

    BINARY_NAME = 'ccellular'
    BINARY_VERSION = '1.0'
    DISTRIBUTION_NAME = 'sawtooth-ccellular'
    VALIDATOR_URL = 'tcp://localhost:4004'


    CLIENT_URL = 'http://192.168.99.101:8008'
    CLIENT_KEY_PATH = '~/.sawtooth/keys/' + getpass.getuser() + '.priv'

    # SHOULD NOT BE CHANGED AT RUNTIME
    FAMILY_NAME = 'ccellular'
    FAMILY_VERSION = '1.0'


# Hack, sorry
DatabaseManagerConfig.DISTRIBUTED_MANAGER_NAME = DistributedManagerConfig.NAME