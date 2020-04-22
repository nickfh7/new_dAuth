from dAuth.ccellular import CCellular
from dAuth.managers import NetworkManager, TestManager, TestDatabaseManager, TestDistributedManager
from dAuth.proto.test_proto import TestDatabaseOperation
from dAuth.config import NetworkManagerConfig


# Uses the test managers to check that the framework is functional
def run_multi_node_test(config, num_nodes=3):
    print("Running multi node test with " + str(num_nodes) + " nodes")
    cc = CCellular(config, logging_active=True)
    dbms = []
    nodes = []

    # Make db/dst managers in pairs
    for i in range(num_nodes):
        dbm = TestDatabaseManager(None, name="DBM" + str(i), distributed_manager_name="DSTM" + str(i))
        dstm = TestDistributedManager(None, name="DSTM" + str(i), database_manager_name="DBM" + str(i))
        dbms.append(dbm)
        nodes.append(dstm)
        cc.add_manager(dbm)
        cc.add_manager(dstm)

    # Make dst nodes aware of each other
    for node in nodes:
        node.set_local_nodes(nodes)

    all_managers = dbms + nodes

    cc.start()

    for m in all_managers:
        m.log_info()

    i = 0

    cc.log("\n\n---------TESTING INSERT 1---------")
    op = {'operation' : 'i', 'key' : '1', 'value' : "test_value_1"}
    dbms[i].simulate_trigger(TestDatabaseOperation(op))

    for m in all_managers:
        m.log_info()

    i = (i + 1) % num_nodes

    cc.log("\n\n---------TESTING INSERT 2---------")
    op = {'operation' : 'i', 'key' : '2', 'value' : "test_value_2"}
    dbms[i].simulate_trigger(TestDatabaseOperation(op))

    for m in all_managers:
        m.log_info()

    i = (i + 1) % num_nodes

    cc.log("\n\n---------TESTING UPDATE 1---------")
    op = {'operation' : 'u', 'key' : '1', 'value' : "test_value_1_update_1"}
    dbms[i].simulate_trigger(TestDatabaseOperation(op))

    for m in all_managers:
        m.log_info()

    i = (i + 1) % num_nodes

    cc.log("\n\n---------TESTING DELETE---------")
    op = {'operation' : 'd', 'key' : '2', 'value' : "DELETE_VALUE_DOES_NOT_MATTER"}
    dbms[i].simulate_trigger(TestDatabaseOperation(op))

    for m in all_managers:
        m.log_info()

    i = (i + 1) % num_nodes

    cc.stop()