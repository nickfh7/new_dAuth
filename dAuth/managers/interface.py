# Managers are used as a standard way of controlling a given feature/service
# All managers should extend the ManagerInterface
# Utilizing start and stop is not necessary, nor is overwriting anything but 'name'

class ManagerInterface:
    # Default attributes
    name = "Unnamed Manager"
    managers = {}
    logger = None


    # --- Control functions ---
    # Called by controlling manager at startup
    def start(self):
        pass

    # Called by controlling manager at shutdown
    def stop(self):
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