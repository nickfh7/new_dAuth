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


# Runs a single instance 
def test_db_single_node():
    print("Running DB single node test")
    # make the configs
    cc_conf = CCellularConfig()
    db_conf = DatabaseManagerConfig()
    dst_conf = DistributedManagerConfig()

    # Set appropriate configurations
    cc_conf.OUTPUT_DIR = "./output/tests/db_single_node"
    db_name = "DB Manager"
    db_conf.NAME = db_name
    dst_name = "DST Manager"
    dst_conf.NAME = dst_name
    db_conf.DISTRIBUTED_MANAGER_NAME = dst_name
    dst_conf.DATABASE_MANAGER_NAME = db_name

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

    assert db.database_get("test_key_1")['imsi'] is "1"
    assert db.database_get("test_key_2")['imsi'] is "1"

    # Update the data
    db.database_update("test_key_1", {"imsi": "2"})
    db.database_update("test_key_2", {"imsi": "3"})

    assert db.database_get("test_key_1")['imsi'] is "2"
    assert db.database_get("test_key_2")['imsi'] is "3"

    # Delete the data
    db.database_delete("test_key_1")
    db.database_delete("test_key_2")

    assert db.database_delete("test_key_1") is None
    assert db.database_delete("test_key_2") is None

    print(" Test success!")

    cc.stop()


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
        cc_conf.OUTPUT_DIR = "./output/tests/db_multi_node_" + str(i)
        db_name = "DB Manager"
        db_conf.NAME = db_name
        dst_name = "DST Manager"
        dst_conf.NAME = dst_name
        db_conf.DISTRIBUTED_MANAGER_NAME = dst_name
        dst_conf.DATABASE_MANAGER_NAME = db_name

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
        assert res1 is not None and res1['imsi'] is "1"
        assert res2 is not None and res2['imsi'] is "1"

    # Update the data
    db.database_update("test_key_1", {"imsi": "2"})
    db.database_update("test_key_2", {"imsi": "3"})

    time.sleep(2)

    for db in dbs:
        res1 = db.database_get("test_key_1")
        res2 = db.database_get("test_key_2")
        assert res1 is not None and res1['imsi'] is "2"
        assert res2 is not None and res2['imsi'] is "3"

    # Delete the data
    db.database_delete("test_key_1")
    db.database_delete("test_key_2")

    time.sleep(2)

    for db in dbs:
        assert db.database_delete("test_key_1") is None
        assert db.database_delete("test_key_2") is None


    print(" Test success!")

    for cc in ccs:
        cc.stop()


def run_tests():
    test_db_single_node()
    test_db_multi_node()