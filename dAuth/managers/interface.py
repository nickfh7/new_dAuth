# Managers are used as a standard way of controlling a given feature/service
# All managers should extend the ManagerInterface
# Utilizing start and stop is not necessary, nor is overwriting anything but 'name'

class ManagerInterface:
    # Default attributes
    name = "Unnamed Manager"
    managers = {}
    logger = None

    def __init__(self, conf=None, name=None):
        self.id = None
        if name:
            self.name = name
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