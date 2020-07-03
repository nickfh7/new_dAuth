from sawtooth_sdk.processor.core import TransactionProcessor

from dAuth.managers.interface import DistributedManagerInterface
from dAuth.config import DistributedManagerConfig
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.sawtooth.client import CCellularClient
from dAuth.sawtooth.handler import CCellularHandler

class DistributedManager(DistributedManagerInterface):
    def __init__(self, conf: DistributedManagerConfig):
        super().__init__(conf)

        self.conf = conf
        
        # Set up transaction processor
        self.transaction_processor = TransactionProcessor(url=conf.VALIDATOR_URL)
        self.handler = CCellularHandler(conf)
        self.handler.set_apply_callback(self.report_update)
        self.transaction_processor.add_handler(self.handler)

        self.client = CCellularClient(conf)

        # Set loggers
        self.handler.logger = self.log
        self.client.logger = self.log

    def run_main(self):
        print("Running dAuth Transaction Processor, Ctr-c to stop")
        self.transaction_processor.start()  # blocking
        print("\nStopping")
        self.transaction_processor.stop()   # make sure to close out connection


    # called on startup from central manager
    def _start(self):
        self.log("Connecting to validator at " + str(self.conf.VALIDATOR_URL))

        # send a thread to the transaction batcher
        self.client.start_batcher(self.is_running)

    # Get the entry from system state
    def get_entry(self, key):
        return self.client.get(key)

    # Update the entry in the system state
    def update_entry(self, entry:DatabaseEntry):
        self.client.set_entry(entry)

    # Returns all key values from the system state
    def get_all_keys(self):
        return [] # TODO

    def report_update(self, entry:DatabaseEntry):
        self.log("New update reported: " + str(entry.key()))

    def is_running(self):
        return self._running