from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InternalError

from dAuth.config import DistributedManagerConfig
from dAuth.proto.database import DatabaseOperation
from dAuth.sawtooth.transactions import unpack_transaction, get_state_data, set_state_data, get_prefix


class CCellularHandler(TransactionHandler):
    def __init__(self, conf:DistributedManagerConfig):
        self.conf = conf
        self.apply_callback = None
        self.logger = None


    # Sets the function to call when handler is used
    def set_apply_callback(self, callback_func):
        self.apply_callback = callback_func
    

    @property
    def family_name(self):
        return self.conf.FAMILY_NAME

    @property
    def family_versions(self):
        return [self.conf.FAMILY_VERSION]

    @property
    def namespaces(self):
        return [get_prefix()]

    def apply(self, transaction, context):
        self.log("Apply called")

        # unpack transaction info
        action, key, data = unpack_transaction(transaction)

        # get the current state
        state = get_state_data(key, context)

        if action == 'set':
            self.log(" Action is 'set'")
            # use protobuf data to create a DatabaseOperation and execute it
            operation = DatabaseOperation(data)

            try:
                self.apply_callback(operation)
            except ValueError:
                self.log(" Database operation failed")

            # update the state
            updated_state = dict(state.items())
            updated_state[key] = data
            set_state_data(key, updated_state, context)

        else:
            raise InternalError('Invalid function requested to be executed by CCellular Handler')

    def log(self, message):
        if self.logger:
            self.logger("(Handler) " + message)