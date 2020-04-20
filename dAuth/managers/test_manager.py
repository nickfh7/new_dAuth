from dAuth.managers.interface import ManagerInterface

# Simple generic test manager
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

    # Returns a dict of basic info
    def info(self):
        return {
            "name" : self.name,
            "logger" : str(self.logger),
            "running" : str(self._running),
            "modules" : str(self.modules.keys()),
        }

    def log_info(self, info):
        info = ["Info for manager:"]
        info.extend(["{0} - {1}".format(k, v) for k, v in self.info().items()])
        self.log("\n   ".join(info))


# Test manager that emulates a basic database setup
# Allows for random database triggering
class TestDatabaseManager(TestManager):
    name = "Test Database Manager"

    def __init__(self, name=None, distributed_manager_name=TestDistributedManager.name):
        super().__init__(name=name)
        self._database = {}  # simple kv database
        self.distributed_manager = None
        self.distributed_manager_name= distributed_manager_name


    # --- Control methods ---
    # Connect to database and start triggers
    def start(self):
        self.log("Starting database and setting triggers")

    # Stop connection and release triggers
    def stop(self):
        self.log("Starting database and setting triggers")


    # --- Exterior methods ---
    # Executes a database operation on the local database
    # This should be called when an operation originated *remotely*
    def execute_operation(self, operation):
        pass


    # --- Interior methods ---
    # Handles a trigger on a local operation
    # This should be called when the operation originated *locally*
    def new_local_operation(self, operation):
        pass

    def info(self):
        info = super().info()
        info['database'] = self._database
        info['distributed_name'] = self.distributed_manager_name
        info['distributed_manager'] = self.distributed_manager
        return info


# Test manager that emulates a basic distributed node
class TestDistributedManager(TestManager):
    name = "Test Distributed Manager"

    def __init__(self, name=None, database_manager_name=TestDatabaseManager.name):
        super().__init__(name=name)
        self._known_operations = {}  # A dict of known propigated operations
        self.database_manager = None
        self.database_manager_name = database_manager_name


    # --- Control methods ---
    # Starts node and connects to other nodes
    def start(self):
        if not self._running:
            self._running = True
            self.log("Starting distributed node")

            # Get the database manager
            self.database_manager = self.get_manager(self.database_manager_name)

            if not self.database_manager:
                self.log("Failed to find database manager")
        else:
            self.log("Distibuted node is already running")

    # Stops node
    def stop(self):
        if not self._running:
            self._running = True
            self.log("Stopping distributed node")
        else:
            self.log("Distibuted node is already running")


    # --- Exterior methods ---
    # Used to send out an operation to other nodes
    def propigate_operation(self, operation):
        self.log("Propigating operation")

    # --- Interior methods ---
    # Handles a newly received remote operation 
    def new_remote_operation(self, operation):
        pass

    def info(self):
        info = super().info()
        info['known_operations'] = self._known_operations
        info['database_manager_name'] = self.database_manager_name
        info['database_manager'] = self.database_manager
        return info
