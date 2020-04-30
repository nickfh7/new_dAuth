from dAuth.proto.database import DatabaseOperation
from dAuth.config import DatabaseManagerConfig, DistributedManagerConfig

# Managers are used as a standard way of controlling a given feature/service
# All managers should extend the ManagerInterface (or appropriate sub-interface)
# Utilizing start and stop is not necessary, nor is overwriting anything but 'name'


# Base manager interface
# Provides basic functionality: 
#  - start/stop functions (overwrite _start/_stop)
#  - basic central manager interactions (get other managers, set logger)
#  - logging via the set logger (usually handled by the central manager)
class ManagerInterface:
    # Default attributes
    name = "Unnamed Manager"
    managers = {}
    logger = None

    def __init__(self, conf):
        self.conf = conf
        self.id = None
        self.name = conf.NAME
        self._running = False


    # Used by the central manager if the main thread of execution should 
    # be here while running (i.e. this function blocks)
    def run_main(self):
        raise NotImplementedError("This manager does not support run_main")


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

    # Called by controlling manager to set available manager list
    def set_available_managers(self, managers):
        self.managers = managers

    # Called by contolling manager to capture logging
    # Logger function is of the form func(name, message)
    def set_logger(self, logger_function):
        self.logger = logger_function

    
    # --- Manager functions ---
    # Used by the manager get access to another manager
    def get_manager(self, name):
        manager = self.managers.get(name)
        if manager is None:
            self.log("Manager not found: " + name)
            return

        return manager

    # Sends a message to the logger
    def log(self, message):
        if self.logger:
            self.logger(self.name, message)
        else:
            print("<{0}> {1}".format(self.name, message))

    # Returns a dict of basic info
    def info(self):
        return {
            "name" : self.name,
            "logger" : str(self.logger),
            "running" : str(self._running),
            "managers" : str(", ".join(self.managers.keys())),
        }

    # Logs the info dict
    def log_info(self):
        info = ["Info for " + self.name + ":"]
        info.extend(["{0} - {1}".format(k, v) for k, v in self.info().items()])
        self.log("\n   ".join(info))


# Standard interface for database management
# Provides methods for executing remote and propagating local operations
class DatabaseManagerInterface(ManagerInterface):
    name = DatabaseManagerConfig.NAME

    def __init__(self, conf:DatabaseManagerConfig):
        super().__init__(conf)

    # Required function for executing remote operations
    def execute_operation(self, operation: DatabaseOperation):
        raise NotImplementedError()

    # Required function for propagating local operations
    def new_local_operation(self, operation: DatabaseOperation):
        raise NotImplementedError()


# Standard interface for distributed management
# Provides methods for passing along remote and propagating out operations
class DistributedManagerInterface(ManagerInterface):
    name = DistributedManagerConfig.NAME

    def __init__(self, conf:DistributedManagerConfig):
        super().__init__(conf)

    # Required function for propagating local operations
    def propagate_operation(self, operation: DatabaseOperation):
        raise NotImplementedError()
        
    # Required function for passing remote operations
    def new_remote_operation(self, operation: DatabaseOperation):
        raise NotImplementedError()