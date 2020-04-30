import logging
import os

from dAuth.config import CCellularConfig
from dAuth.utils import random_string

# CCellular is the central manager of dAuth
# It starts and facilitates all other managers
class CCellular:
    def __init__(self, conf:CCellularConfig):
        self.conf = conf

        self.id = conf.ID or random_string()  # generate random id if one is not configured

        # a mapping of manager names to managers
        self.managers = {}

        # logging
        if conf.LOGGING_ENABLED:
            logger = logging.getLogger("ccellular-" + self.id)
            logger.setLevel(logging.DEBUG)
            os.makedirs(conf.OUTPUT_DIR, exist_ok=True)
            fh = logging.FileHandler(os.path.join(conf.OUTPUT_DIR, "ccellular.log"))
            fh.setLevel(logging.DEBUG)
            logger.addHandler(fh)
            self.local_logger = logger.debug
        else:
            self.local_logger = None
        
        self.remote_logger = None

        # internal
        self._running = False
        self.log("CCellular is running with ID: " + self.id)

    # Starts all managers
    def start(self):
        self.log("Start called")
        if not self._running:
            self._running = True
            for name, manager in self.managers.items():
                self.log(" Starting manager: " + name)
                try:
                    manager.start()
                except Exception as e:
                    self.log(' Failed to start: ' + manager.name + " - " + str(e))

            # If a run function has been specified, use it
            if self.conf.RUN_FUNCTION is not None:
                self.log("Starting run function")
                self.conf.RUN_FUNCTION()
        else:
            self.log(" Already running")

    # Stops all manages
    def stop(self):
        self.log("Stop called")
        if self._running:
            self._running = True
            for name, manager in self.managers.items():
                self.log("Stopping manager: " + name)
                try:
                    manager.stop()
                except Exception as e:
                    self.log('Failed to stop: ' + name + " - " + str(e))
        else:
            self.log(" Not running")

    # Adds a manager to the set of managers
    def add_manager(self, manager, replace=False):
        self.log("Adding manager: " + manager.name)

        # Check for existing manager first
        if manager.name in self.managers:
            self.log(" Manager already exists")
            if replace:
                self.log(" Replacing Manager")
                if self._running:
                    self.managers[manager.name].stop()
            else:
                # TODO: throw exception?
                self.log(" Not replacing")
                return

        # Add and initialize manager, start if already running
        self.managers[manager.name] = manager
        manager.id = self.id
        manager.set_logger(self._double_log)
        manager.set_available_managers(self.managers)
        if self._running:
            manager.start()

    # Log the message
    def log(self, message):
        if self.id:
            self._double_log("CCellular:"+self.id, message)
        else:
            self._double_log("CCellular", message)

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