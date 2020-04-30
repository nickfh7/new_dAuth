import time
import json
import copy
import pytest

from dAuth.config import CCellularConfig, DatabaseManagerConfig, DistributedManagerConfig
from dAuth.proto.database import DatabaseOperation
from dAuth.ccellular import CCellular
from dAuth.managers import DatabaseManager, TestDistributedManager
from dAuth.database import operations_cli

# Tests for the database will use the test distributed manager


# Runs a single instance and checks that operations work
def test_db_single_node():
    print("Running DB single node test")
    # make the configs
    cc_conf = CCellularConfig()
    db_conf = DatabaseManagerConfig()
    dst_conf = DistributedManagerConfig()

    # Set appropriate configurations
    cc_conf.OUTPUT_DIR = "./output/tests/database/db_single_node"

    db_conf.DATABASE_NAME = "testing_db"
    db_conf.COLLECTION_NAME = "single_node_test"

    # Build managers and add them
    cc = CCellular(cc_conf)
    db = DatabaseManager(db_conf)
    dst = TestDistributedManager(dst_conf)
    cc.add_manager(db)
    cc.add_manager(dst)

    # Start ccellular
    cc.start()

    # Test a couple of inserts
    db.database_insert("test_key_1", {"imsi": "1"})
    db.database_insert("test_key_2", {"imsi": "1"})

    assert db.database_get("test_key_1")['imsi'] == "1"
    assert db.database_get("test_key_2")['imsi'] == "1"

    # Update the data
    db.database_update("test_key_1", {"imsi": "2"})
    db.database_update("test_key_2", {"imsi": "3"})

    assert db.database_get("test_key_1")['imsi'] == "2"
    assert db.database_get("test_key_2")['imsi'] == "3"

    # Delete the data
    db.database_delete("test_key_1")
    db.database_delete("test_key_2")

    assert db.database_delete("test_key_1") is None
    assert db.database_delete("test_key_2") is None

    print(" Test success!")

    cc.stop()


# runs multiple instances and checks that:
#  - db operations work
#  - db operations are propagated from originator
def test_db_multi_node(num_nodes=3):
    print("Running DB multi node test")

    ccs = []
    dbs = []
    dsts = []

    # Set up nodes
    for i in range(num_nodes):
        # make the configs
        cc_conf = CCellularConfig()
        db_conf = DatabaseManagerConfig()
        dst_conf = DistributedManagerConfig()

        # Set appropriate configurations
        cc_conf.OUTPUT_DIR = "./output/tests/database/db_multi_node_" + str(i)

        db_conf.DATABASE_NAME = "testing_db"
        db_conf.COLLECTION_NAME = "multi_node_test_" + str(i)

        # Build managers and add them
        cc = CCellular(cc_conf)
        db = DatabaseManager(db_conf)
        dst = TestDistributedManager(dst_conf)
        cc.add_manager(db)
        cc.add_manager(dst)

        ccs.append(cc)
        dbs.append(db)
        dsts.append(dst)

    # Add nodes to each dst
    for dst in dsts:
        dst.add_nodes(dsts)

    # Start ccellular
    for cc in ccs:
        cc.start()

    main_db = dbs[0]

    # Clear any previous data
    main_db.database_delete("test_key_1")
    main_db.database_delete("test_key_2")

    time.sleep(2)

    for db in dbs:
        assert db.database_delete("test_key_1") is None
        assert db.database_delete("test_key_2") is None

    # Test a couple of inserts
    main_db.database_insert("test_key_1", {"imsi": "1"})
    main_db.database_insert("test_key_2", {"imsi": "1"})

    time.sleep(2)

    for db in dbs:
        res1 = db.database_get("test_key_1")
        res2 = db.database_get("test_key_2")
        assert res1 is not None and res1['imsi'] == "1"
        assert res2 is not None and res2['imsi'] == "1"

    # Update the data
    main_db.database_update("test_key_1", {"imsi": "2"})
    main_db.database_update("test_key_2", {"imsi": "3"})

    time.sleep(2)

    for db in dbs:
        res1 = db.database_get("test_key_1")
        res2 = db.database_get("test_key_2")
        assert res1 is not None and res1['imsi'] == "2"
        assert res2 is not None and res2['imsi'] == "3"

    # Delete the data
    main_db.database_delete("test_key_1")
    main_db.database_delete("test_key_2")

    time.sleep(2)

    for db in dbs:
        assert db.database_delete("test_key_1") is None
        assert db.database_delete("test_key_2") is None


    print(" Test success!")

    for cc in ccs:
        cc.stop()


# Checks performance of propagation between two nodes
def test_db_propagation_performance(duration=5):
    print("Running DB propagation performance test")
    print(" Duration: {}s".format(duration))

    ccs = []
    dbs = []
    dsts = []

    # Set up nodes
    for i in range(2):
        # make the configs
        cc_conf = CCellularConfig()
        db_conf = DatabaseManagerConfig()
        dst_conf = DistributedManagerConfig()

        # Set appropriate configurations
        cc_conf.OUTPUT_DIR = "./output/tests/database/db_propagation_performance_" + str(i)
        cc_conf.LOGGING_ENABLED = False

        db_conf.DATABASE_NAME = "testing_db"
        db_conf.COLLECTION_NAME = "multi_node_test_performance_" + str(i)

        # Build managers and add them
        cc = CCellular(cc_conf)
        db = DatabaseManager(db_conf)
        dst = TestDistributedManager(dst_conf)
        cc.add_manager(db)
        cc.add_manager(dst)

        ccs.append(cc)
        dbs.append(db)
        dsts.append(dst)

    # Add nodes to each dst
    for dst in dsts:
        dst.add_nodes(dsts)

    # Start ccellular
    for cc in ccs:
        cc.start()

    main_db = dbs[0]
    other_db = dbs[1]

    start = time.time()
    last_check = time.time()

    total_inserts = 0
    i = 0
    while time.time() - start < duration:
        # Do insert
        main_db.database_insert("test_key_{0}".format(i), {"imsi": "12345"})
        i += 1
        total_inserts += 1

    res = []

    total_main = main_db.collection.count({"imsi": "12345"})
    total_other = other_db.collection.count({"imsi": "12345"})

    print(" Done inserting into main db, other db likley still getting propagations")
    print(" {0} total inserted in main db (originator), inserts on remote: {1}".format(total_main, total_other))

    print(" Tracking propagation speed of remaing inserts")
    start = time.time()
    while total_main > other_db.collection.count({"imsi": "12345"}):
        time.sleep(0.001)

    stop = time.time()
    print(" Speed of propagation: {0} op/s".format((total_main-total_other)/(stop-start)))

    print(" Stopping managers and cleaning up collections...")
    for cc in ccs:
        cc.stop()

    for i in range(total_inserts):
        for db in dbs:
            db.database_delete("test_key_{0}".format(i))

    print(" All test data deleted, test complete")


def run_tests():
    # test_db_single_node()
    test_db_multi_node()
    # test_db_propagation_performance()

