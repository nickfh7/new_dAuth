from dAuth.managers.interface import ManagerInterface


# Simple test manager
class TestManager(ManagerInterface):
    name = "Test Manager"
    def __init__(self, name=None):
        if name:
            self.name = name
        self._running = False

    def start(self):
        self._running = True
        self.log("Start called")

    def stop(self):
        self._running = False
        self.log("Stop called")

    def info(self):
        self.log("\n   ".join(["Info for interface:", 
                               "name - " + self.name,
                               "logger - " + str(self.logger),
                               "running - " + str(self._running),
                               "modules - " + str(self.modules.keys()),
                               ]))
