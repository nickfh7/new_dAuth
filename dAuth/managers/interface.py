# Managers are used as a standard way of controlling a given module
# Managers should use the ManagerInterface

class ManagerInterface:
    # Default attributes
    name = "Unnamed Manager"
    modules = {}
    logger = None


    # --- Control functions ---
    # Called by controlling module at startup
    def start(self):
        pass

    # Called by controlling module at shutdown
    def stop(self):
        pass

    # Called by controlling module to set available module list
    def set_modules(self, modules):
        self.modules = modules

    # Called by contolling module to capture logging
    # Logger function is of the form func(name, message)
    def set_logger(self, logger_function):
        self.logger = logger_function

    
    # --- Module functions ---
    # Used by the manager get another manager
    def get_module(self, module_name):
        module = self.modules.get(module_name)
        if module is None:
            self.log()

        return module

    # Sends a message to the logger
    def log(self, message):
        if self.logger:
            self.logger(self.name, message)
        else:
            print("<{0}> {1}".format(self.name, message))