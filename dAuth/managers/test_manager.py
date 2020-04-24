import copy

from dAuth.managers.interface import DistributedManagerInterface, DatabaseManagerInterface, ManagerInterface
from dAuth.proto.database import DatabaseOperation
from dAuth.utils import random_string
from dAuth.config import DatabaseManagerConfig, DistributedManagerConfig

# Simple generic test manager
class TestManager(ManagerInterface):
    name = "Test Manager"
    def __init__(self, conf):
        super().__init__(conf)

    def _start(self):
        self.log("_start called in TestManager")

    def _stop(self):
        self.log("_stop called in TestManager")


# Test manager that emulates a basic database setup
# Allows for random database triggering
# !!!!!! BROKEN !!!!!!  Needs conf update
class TestDatabaseManager(DatabaseManagerInterface):
    name = "Test Database Manager"

    def __init__(self, conf):
        super().__init__(conf)
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
class TestDistributedManager(DistributedManagerInterface):
    name = "Test Distributed Manager"

    def __init__(self, conf:DistributedManagerConfig):
        super().__init__(conf)
        self._known_operations = {}  # A dict of known propagated operations
        self._nodes = []  # list of nodes to talk to
        self.database_manager = None


    # --- Control methods ---
    # Starts node and connects to other nodes
    def _start(self):
        # Get the database manager
        self.database_manager = self.get_manager(self.conf.DATABASE_MANAGER_NAME)

    # Stops node
    def _stop(self):
        pass


    # --- Exterior methods ---
    # Used to send out an operation to other nodes
    def propagate_operation(self, operation: DatabaseOperation):
        # Should not have an op_id yet if its local
        if operation.op_id is not None and operation.op_id in self._known_operations:
            self.log("!!! op_code has already been used, possible db replay check failure")
            return

        # Set op_id
        operation.op_id = random_string()

        self.log("Propagating local operation")
        if operation.op_id not in self._known_operations:
            self._known_operations[operation.op_id] = operation
            for node in self._nodes:
                if node.id is not self.id:
                    node.new_remote_operation(operation)
        else:
            self.log(" Operation already propagated, ignoring")
        

    # --- Interior methods ---
    # Handles a newly received remote operation 
    def new_remote_operation(self, operation: DatabaseOperation):
        self.log("New remote operation from " + operation.ownership())

        # Check that this operation hasn't been seen before
        if operation.op_id not in self._known_operations:
            # execute the operation locally
            if self.database_manager is not None:
                self._known_operations[operation.op_id] = operation
                self.database_manager.execute_operation(operation)
            else:
                self.log(" No database manager to execute remote operation")
        else:
            self.log(" Operation already received, ignoring")

    # Used in testing to add other nodes    
    def add_nodes(self, nodes:list):
        if type(nodes) is not list:
            raise ValueError("Expected list of nodes")

        self._nodes.extend(nodes)

    def info(self):
        info = super().info()
        info['known_operations'] = self._known_operations
        info['other_nodes'] = ", ".join([n.name for n in self._nodes])
        info['database_manager_name'] = self.conf.DATABASE_MANAGER_NAME
        info['database_manager'] = self.database_manager
        return info
