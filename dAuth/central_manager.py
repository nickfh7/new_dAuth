import logging
import os

from dAuth.managers import DatabaseManager, DistributedManager, SyncManager
from dAuth.config import CentralManagerConfig
from dAuth.utils import random_string


# It starts and facilitates all other managers
class CentralManager:
    def __init__(self, conf:CentralManagerConfig):
        self.conf = conf

        self.id = conf.ID or random_string()  # generate random id if one is not configured

        self.database_manager = None
        self.distributed_manager = None
        self.sync_manager = None

        # logging
        if conf.LOGGING_ENABLED:
            logger = logging.getLogger("central_manager-" + self.id)
            logger.setLevel(logging.DEBUG)
            os.makedirs(conf.OUTPUT_DIR, exist_ok=True)
            fh = logging.FileHandler(os.path.join(conf.OUTPUT_DIR, "central_manager.log"))
            fh.setLevel(logging.DEBUG)
            logger.addHandler(fh)
            self.local_logger = logger.debug
        else:
            self.local_logger = None
        
        self.remote_logger = None

        # internal
        self._running = False
        self.log("Central Manager created with ID: " + self.id)

    # Creates the managers with the corresponding configs
    # Must be called before start
    def init_managers(self, dbm_conf, dist_conf, sync_conf, nwm_config):
        self.database_manager = DatabaseManager(dbm_conf)
        self.distributed_manager = DistributedManager(dist_conf)
        self.sync_manager = SyncManager(sync_conf)

        self.database_manager.set_logger(self._double_log)
        self.distributed_manager.set_logger(self._double_log)
        self.sync_manager.set_logger(self._double_log)

        self.sync_manager.set_managers(self.distributed_manager, self.database_manager)

    # Starts all managers
    def start(self):
        self.log("Start called")
        if not self._running:
            self._running = True

            self.log("Starting all managers")
            try:
                self.database_manager.start()
                self.distributed_manager.start()
                self.sync_manager.start()
                # self.network_manager.start()
            except Exception as e:
                self.log(" Failed to start managers: " + str(e))

            # Run the distributed manager's client
            self.distributed_manager.run_main()
        else:
            self.log(" Already running")

    # Stops all managers
    def stop(self):
        self.log("Stop called")
        if self._running:
            self._running = True

            self.log("Stopping all managers")
            try:
                self.database_manager.stop()
                self.distributed_manager.stop()
                self.sync_manager.stop()
                # self.network_manager.stop()
            except Exception as e:
                self.log(" Failed to stop managers: " + str(e))
        else:
            self.log(" Not running")

    # Log the message
    def log(self, message):
        if self.id:
            self._double_log("Central Manager:"+self.id, message)
        else:
            self._double_log("Central Manager", message)

    # Sends message to local and/or remote logger
    def _double_log(self, category, message):
        if self.conf.LOGGING_ENABLED:
            if self.local_logger:
                self.local_logger("<{0}> {1}".format(category, message))
            if self.remote_logger:
                self.remote_logger(category, message)

    # Debug logging function, simply prints
    @staticmethod
    def _debug_log(category, message):
        print("<{0}> {1}".format(category, message))