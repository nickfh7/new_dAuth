# This file contains global configuration objects
# Default values should be set here
# Values can be changed at runtime via parser/input (TODO)

import random
import string


def random_string(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


# Used for anything not tied to a particular manager
class CCellularConfig:
    # Randomly generate id
    ID = random_string()


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

