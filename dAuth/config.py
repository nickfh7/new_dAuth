import getpass

# This file contains global configuration objects
# Default values should be set here
# In the main file, an instance of each of these should be made 
#  and given to the respective manager
# Values can be changed at runtime via parser


# Used for anything not tied to a particular manager
class CentralManagerConfig:
    NAME = "Central Manager"

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


class DistributedManagerConfig:
    NAME = "Distributed Manager"

    DISTRIBUTION_NAME = 'sawtooth-ccellular'
    VALIDATOR_URL = 'tcp://localhost:4004'

    CLIENT_URL = 'localhost:8008'
    CLIENT_KEY_PATH = "/home/" + getpass.getuser() + "/.sawtooth/keys/" + getpass.getuser() + ".priv"

    # SHOULD NOT BE CHANGED AT RUNTIME
    FAMILY_NAME = 'ccellular'
    FAMILY_VERSION = '1.0'

    # Batch configurations
    BATCH_SIZE = 10           # Max size for a batch
    BATCH_TIMEOUT = 5         # timeout before sending whatever transaction are available
    BATCH_CHECK_DELAY = 0.01  # delay between checking for new transactions


class SyncManagerConfig:
    NAME = "Sync Manager"
