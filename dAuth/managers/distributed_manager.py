from sawtooth_sdk.processor.core import TransactionProcessor

from dAuth.managers.interface import DistributedManagerInterface
from dAuth.config import DistributedManagerConfig
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.sawtooth.client import CCellularClient
from dAuth.sawtooth.handler import CCellularHandler
from dAuth.sawtooth.event_listener import EventListener

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

        self.trigger_callback_func = None

        self.event_listener = EventListener(self.conf)
        self.event_listener.set_logger(self.log)

    # Blocking function that runs the transaction processor
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
        self.event_listener.start()

    def _stop(self):
        self.event_listener.stop()

    # Get the entry from system state
    def get_entry(self, key):
        self.log("Getting entry for key: " + str(key))
        return self.client.get(key)

    # Update the entry in the system state
    def update_entry(self, entry:DatabaseEntry):
        self.log("Updating entry: " + str(entry.to_dict()))
        self.client.set_entry(entry)

    # Returns all key values from the system state
    def get_all_keys(self):
        self.log("Retrieving all keys")
        return self.client.get_all()

    # Sets a callback function called when new data is available
    # for a given key (the key is passed as an arg to the callback)
    def set_report_callback(self, callback_func):
        self.log("Report callback set")
        self.trigger_callback_func = callback_func

    # Called when new data is available for a key, and will pass 
    # the key back through the callback function if it is set
    def report_update(self, key):
        self.log("New update reported: " + str(key))
        if self.trigger_callback_func:
            self.trigger_callback_func(key)

    # Returns the number of all keys available
    def count(self):
        return len(self.get_all_keys())

    def is_running(self):
        return self._running