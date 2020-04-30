

from sawtooth_sdk.processor.core import TransactionProcessor

from dAuth.managers.interface import DistributedManagerInterface
from dAuth.config import DistributedManagerConfig
from dAuth.proto.database import DatabaseOperation
from dAuth.sawtooth.client import CCellularClient
from dAuth.sawtooth.handler import CCellularHandler

class DistributedManager(DistributedManagerInterface):
    def __init__(self, conf: DistributedManagerConfig):
        super().__init__(conf)

        self.conf = conf
        
        # Set up transaction processort
        self.transaction_processor = TransactionProcessor(url=conf.VALIDATOR_URL)
        self.handler = CCellularHandler(conf)
        self.handler.set_apply_callback(self.new_remote_operation)
        self.transaction_processor.add_handler(self.handler)

        self.client = CCellularClient(conf)

        # Set at start
        self.database_manager = None

        # Set loggers
        self.handler.logger = self.log
        self.client.logger = self.log

    def run_main(self):
        print("Running CCellular Transaction Processor, Ctr-c to stop")
        self.transaction_processor.start()  # blocking
        print("\nStopping")
        self.transaction_processor.stop()   # make sure to close out connection


    def _start(self):
        # get the current database manager
        self.log("Connecting to validator at " + str(self.conf.VALIDATOR_URL))
        self.database_manager = self.get_manager(self.conf.DATABASE_MANAGER_NAME)


    # Uses the sawtooth client to create and send a new transaction
    def propagate_operation(self, operation: DatabaseOperation):
        self.log("Propagating operation, sending to client")
        self.client.set_operation(operation)
        
    # Transaction processor uses this (via its handler)
    def new_remote_operation(self, operation: DatabaseOperation):
        if operation.ownership() == self.id:
            self.log("Avoiding replay of operation - " + str(operation.key()) + ", " + str(operation.operation()))
            raise ValueError("Replay value")

        self.log("New remote operation, passing to Database Manager")
        if self.database_manager:
            self.database_manager.execute_operation(operation)
        else:
            self.log(" No Database Manager")
