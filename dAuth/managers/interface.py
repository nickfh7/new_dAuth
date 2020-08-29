from dAuth.config import DatabaseManagerConfig, DistributedManagerConfig

# Managers are used as a standard way of controlling a given feature/service
# All managers should extend the ManagerInterface (or appropriate sub-interface)
# Utilizing start and stop is not necessary, nor is overwriting anything but 'name'


# Base manager interface
# Provides basic functionality: 
#  - start/stop functions (overwrite _start/_stop)
#  - logging via the set logger (usually handled by the central manager)
class ManagerInterface:
    # Default attributes
    name = "Unnamed Manager"
    logger = None

    def __init__(self, conf):
        self.conf = conf
        self.id = None
        self.name = conf.NAME
        self._running = False

    # --- Control functions ---
    # Called by controlling manager at startup
    def start(self):
        if not self._running:
            self.log("Starting " + self.name)
            self._running = True

            self._start()

        else:
            self.log(self.name + " is already running")

    def _start(self):
        pass

    # Called by controlling manager at shutdown
    def stop(self):
        if self._running:
            self.log("Stopping " + self.name)
            self._running = False

            self._stop()

        else:
            self.log(self.name + " is not running")

    def _stop(self):
        pass

    # Called by contolling manager to capture logging
    # Logger function is of the form func(name, message)
    def set_logger(self, logger_function):
        self.logger = logger_function

    # Called by controlling manager to set id
    def set_id(self, id):
        self.conf.ID = id

    # Sends a message to the logger
    def log(self, message):
        if self.logger:
            self.logger(self.name, message)
        # else:
        #     print("<{0}> {1}".format(self.name, message))


# Standard interface for database management
class DatabaseManagerInterface(ManagerInterface):
    name = DatabaseManagerConfig.NAME

    def __init__(self, conf:DatabaseManagerConfig):
        super().__init__(conf)


# Standard interface for distributed management
class DistributedManagerInterface(ManagerInterface):
    name = DistributedManagerConfig.NAME

    def __init__(self, conf:DistributedManagerConfig):
        super().__init__(conf)