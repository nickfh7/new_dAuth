from dAuth.ccellular import CCellular
from dAuth.managers import NetworkManager, TestManager, TestDatabaseManager, TestDistributedManager
from dAuth.proto.test_proto import TestDatabaseOperation
from dAuth.config import NetworkManagerConfig

def simple_manager_test(manager_type, test_name, cc_conf):
    print("Running simple test with " + test_name)
    c = CCellular(cc_conf)
    t = manager_type()
    c.add_manager(t)
    t.log_info()
    c.start()
    t.log_info()
    c.stop()
    t.log_info()

def multiple_simple_manager_test(manager_type, test_name, cc_conf):
    print("Running multiple simple test with " + test_name)
    c = CCellular(cc_conf)
    t = manager_type()
    c.add_manager(t)
    t.log_info()

    t2 = manager_type(name=manager_type.name + " 2")
    c.add_manager(t2)
    t2.log_info()

    c.start()

    t.log_info()
    t2.log_info()

    c.stop()
    t.log_info()
    t2.log_info()

def run_all_simple_tests(cc_conf):
    for manager_type, name in [(TestManager, "test_manager"),
                         (TestDatabaseManager, "test_database_manager"),
                         (TestDistributedManager, "test_distributed_manager")]:
        cc_conf.OUTPUT_DIR = "output/simple_test/" + name
        simple_manager_test(manager_type, name)
        cc_conf.OUTPUT_DIR = "output/multiple_simple_test/" + name
        multiple_simple_manager_test(manager_type, name)


def run_full_setup(cc_conf):
    c = CCellular(cc_conf)

    c.log("---------STARTING SETUP TEST---------")
    # nwm = NetworkManager(NetworkManagerConfig())
    dbm = TestDatabaseManager()
    dstm = TestDistributedManager()

    # c.add_manager(nwm)
    c.add_manager(dbm)
    c.add_manager(dstm)

    # nwm.log_info()
    dbm.log_info()
    dstm.log_info()

    c.start()

    # nwm.log_info()
    dbm.log_info()
    dstm.log_info()


    # test a basic propagation
    c.log("\n\n---------TESTING LOCAL PROPAGATION---------")
    op1 = {'operation' : 'i', 'key' : '1', 'value' : "test_value_1"}
    dbm.simulate_trigger(TestDatabaseOperation(op1))

    dbm.log_info()
    dstm.log_info()


    c.log("\n\n---------TESTING REMOTE INSERT---------")
    op2 = {'operation' : 'i', 'key' : '2', 'value' : "test_value_2", 'id' : 'remote_id_2', 'remote' : True, 'ownership' : "some_remote_owner"}
    dstm.new_remote_operation(TestDatabaseOperation(op2))

    dbm.log_info()
    dstm.log_info()


    c.log("\n\n---------TESTING REMOTE REINSERT---------")
    dstm.new_remote_operation(TestDatabaseOperation(op2))

    dbm.log_info()
    dstm.log_info()


    c.log("\n\n---------TESTING REMOTE UPDATE---------")
    op3 = {'operation' : 'u', 'key' : '1', 'value' : "test_value_1_updated_1", 'id' : 'remote_id_3', 'remote' : True, 'ownership' : "some_remote_owner"}
    dstm.new_remote_operation(TestDatabaseOperation(op3))

    dbm.log_info()
    dstm.log_info()


    c.log("\n\n---------TESTING REMOTE DELETE---------")
    op4 = {'operation' : 'd', 'key' : '2', 'value' : "DELETE_VALUE_DOESNT_MATTER", 'id' : 'remote_id_4', 'remote' : True, 'ownership' : "some_remote_owner"}
    dstm.new_remote_operation(TestDatabaseOperation(op4))

    dbm.log_info()
    dstm.log_info()

    c.stop()

    dbm.log_info()
    dstm.log_info()


def run_multi_node(cc_conf, num_nodes=3):
    print("Running multi node test with " + str(num_nodes) + " nodes")
    cc_conf.OUTPUT_DIR = './output/multi_node/'
    cc = CCellular(cc_conf)
    dbms = []
    nodes = []

    # Make db/dst managers in pairs
    for i in range(num_nodes):
        dbm = TestDatabaseManager(name="DBM" + str(i), distributed_manager_name="DSTM" + str(i))
        dstm = TestDistributedManager(name="DSTM" + str(i), database_manager_name="DBM" + str(i))
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