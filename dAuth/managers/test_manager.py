import copy

from dAuth.managers.interface import ManagerInterface
from dAuth.proto.database import DatabaseOperation
from dAuth.utils import random_string

# Simple generic test manager
class TestManager(ManagerInterface):
    name = "Test Manager"
    def __init__(self, conf=None, name=None):
        super().__init__(name=name)

    def _start(self):
        self.log("_start called in TestManager")

    def _stop(self):
        self.log("_stop called in TestManager")


# Test manager that emulates a basic database setup
# Allows for random database triggering
class TestDatabaseManager(ManagerInterface):
    name = "Test Database Manager"

    def __init__(self, conf=None, name=None, distributed_manager_name=None):
        super().__init__(name=name)
        self._database = {}  # simple kv database
        self.distributed_manager = None
        self.distributed_manager_name = distributed_manager_name or TestDistributedManager.name


    # --- Control methods ---
    # Connect to database and start triggers
    def _start(self):
        # Get the distributed manager
        self.distributed_manager = self.get_manager(self.distributed_manager_name)

        if self.distributed_manager is None:
            self.log("Failed to find distributed manager")

    # Stop connection and release triggers
    def _stop(self):
        pass


    # --- Exterior methods ---
    # Executes a database operation on the local database
    # This should be called when an operation originated *remotely*
    def execute_operation(self, operation: DatabaseOperation):
        self.log("Executing operation")
        op_type = copy.copy(operation.operation())
        key = copy.copy(operation.key())
        value = copy.deepcopy(operation.to_dict())
        success = False

        if op_type is 'i':
            self.log(" Doing insert operation on " + key)
            if key not in self._database:
                self._database[key] = value
                success = True
            else:
                self.log("  Key already exists, ignoring")
        elif op_type is 'u':
            self.log(" Doing update operation on " + key)
            if key in self._database:
                self._database[key] = value
                success = True
            else:
                self.log("  Key doesn't exist, ignoring")
        elif op_type is 'd':
            self.log(" Doing delete operation on " + key)
            if key in self._database:
                del self._database[key]
                success = True
            else:
                self.log("  Key doesn't exist, ignoring")
        else:
            self.log(" Bad operation type: " + op_type)
        
        if success:
            if not operation.remote():
                self.new_local_operation(operation)
            else:
                self.log(" Operation from remote, not propagating")


    # --- Interior methods ---
    # Handles a trigger on a local operation
    # This should be called when the operation originated *locally*
    def new_local_operation(self, operation: DatabaseOperation):
        self.log("New local operation")
        if self.distributed_manager is not None:
            operation.set_remote(True)
            operation.set_ownership(self.id)
            operation.set_id(random_string(20))
            self.distributed_manager.propagate_operation(operation)
        else:
            self.log(" No distributed manager to propagate local operation")


    # Used in testing for simulating a trigger
    def simulate_trigger(self, operation: DatabaseOperation):
        self.execute_operation(operation)


    def info(self):
        info = super().info()
        info['database'] = self._database
        info['distributed_name'] = self.distributed_manager_name
        info['distributed_manager'] = self.distributed_manager
        return info


# Test manager that emulates a basic distributed node
class TestDistributedManager(ManagerInterface):
    name = "Test Distributed Manager"

    def __init__(self, conf=None, name=None, database_manager_name=None):
        super().__init__(name=name)
        self._known_operations = {}  # A dict of known propagated operations
        self._nodes = {}
        self.database_manager = None
        self.database_manager_name = database_manager_name or TestDatabaseManager.name


    # --- Control methods ---
    # Starts node and connects to other nodes
    def _start(self):
        # Get the database manager
        self.database_manager = self.get_manager(self.database_manager_name)

    # Stops node
    def _stop(self):
        pass


    # --- Exterior methods ---
    # Used to send out an operation to other nodes
    def propagate_operation(self, operation: DatabaseOperation):
        self.log("Propagating local operation")
        if operation.id() not in self._known_operations:
            self._known_operations[operation.id()] = operation.to_dict()
            for node in self._nodes:
                if node.name is not self.name:
                    node.new_remote_operation(operation)
        else:
            self.log(" Operation already propagated, ignoring")
        

    # --- Interior methods ---
    # Handles a newly received remote operation 
    def new_remote_operation(self, operation: DatabaseOperation):
        self.log("New remote operation from " + operation.ownership())
        if operation.id() not in self._known_operations:
            if self.database_manager is not None:
                self._known_operations[operation.id()] = operation.to_dict()
                self.database_manager.execute_operation(operation)
            else:
                self.log(" No database manager to execute remote operation")
        else:
            self.log(" Operation already received, ignoring")

    # Used in testing to add other nodes    
    def set_local_nodes(self, nodes):
        self._nodes = nodes

    def info(self):
        info = super().info()
        info['known_operations'] = self._known_operations
        info['other_nodes'] = ", ".join([n.name for n in self._nodes])
        info['database_manager_name'] = self.database_manager_name
        info['database_manager'] = self.database_manager
        return info
