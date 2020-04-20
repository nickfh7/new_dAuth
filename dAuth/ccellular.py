import logging
import os

# CCellular is the main class of dAuth
# It starts and facilitates all other modules
class CCellular:
    def __init__(self, logfile_dir="./output/ccellular"):
        # a mapping of module names to module interfaces
        self.modules = {}

        # logging
        logger = logging.getLogger("ccellular")
        logger.setLevel(logging.DEBUG)
        os.makedirs(logfile_dir, exist_ok=True)
        fh = logging.FileHandler(os.path.join(logfile_dir, "ccellular.log"))
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        self.local_logger = logger.debug
        self.remote_logger = None

        # internal
        self._running = False

    # Starts all modules
    def start(self):
        self.log("Start called")
        if not self._running:
            self._running = True
            for module_name, module_interface in self.modules.items():
                self.log(" Starting module: " + module_name)
                try:
                    module_interface.start()
                except Exception as e:
                    self.log(' Failed to start: ' + module_name + " - " + str(e))
        else:
            self.log(" Already running")

    # Stops all modules
    def stop(self):
        self.log("Stop called")
        if self._running:
            self._running = True
            for module_name, module_interface in self.modules.items():
                self.log("Stopping module: " + module_name)
                try:
                    module_interface.stop()
                except Exception as e:
                    self.log('Failed to stop: ' + module_name + " - " + str(e))
        else:
            self.log(" Not running")

    # Adds a manager to the set of managers
    def add_manager(self, module, replace=False):
        self.log("Adding module: " + module.name)

        # Check for existing module first
        if module.name in self.modules:
            self.log(" Module already exists")
            if replace:
                self.log(" Replacing module")
                if self._running:
                    self.modules[module.name].stop()
            else:
                # TODO: throw exception?
                self.log(" Not replacing")
                return

        # Add and initialize module, start if already running
        self.modules[module.name] = module
        module.set_logger(self._double_log)
        module.set_modules(self.modules)
        if self._running:
            module.start()

    # Log the message
    def log(self, message):
        self._double_log("CCellular", message)

    # Sends message to local and/or remote logger
    def _double_log(self, category, message):
        if self.local_logger:
            self.local_logger("<{0}> {1}".format(category, message))
        if self.remote_logger:
            self.remote_logger(category, message)

    # Debug logging function, simply prints
    @staticmethod
    def _debug_log(category, message):
        print("<{0}> {1}".format(category, message))