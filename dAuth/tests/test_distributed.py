import time
import threading

from dAuth.ccellular import CCellular
from dAuth.managers import DistributedManager, DatabaseManager
from dAuth.config import DistributedManagerConfig, CCellularConfig, DatabaseManagerConfig

# Simply connects to a single node (can be used with op.sh script or operations cli)
def single_node_test():
    cc_conf = CCellularConfig()
    cc_conf.OUTPUT_DIR = "./output/tests/distributed/single_node"
    cc = CCellular(cc_conf)

    dst_conf = DistributedManagerConfig()
    dst = DistributedManager(dst_conf)
    cc.add_manager(dst)

    dbm_conf = DatabaseManagerConfig
    dbm = DatabaseManager(dbm_conf)
    cc.add_manager(dbm)

    cc_conf.RUN_FUNCTION = dst.run_main
    
    cc.start()  # will block until ctrl-c
    cc.stop()


# Tests a series of inserts, measures the rate at which they occur/propagate
def multi_node_test():
    def run_node(cc_node):
        cc_node.start()  # blocks until ctrl-c
        print("CCellular stopped")
        cc_node.stop()

    threads = []
    dbms = []
    ccs = []
    main_db = None

    for i in range(5):
        cc_conf = CCellularConfig()
        cc_conf.OUTPUT_DIR = "./output/tests/distributed/mulit_node_" + str(i)
        cc_conf.LOGGING_ENABLED = False
        cc = CCellular(cc_conf)
        ccs.append(cc)

        dst_conf = DistributedManagerConfig()
        dst_conf.VALIDATOR_URL = 'tcp://localhost:' + str(4004 + i)
        dst = DistributedManager(dst_conf)
        cc.add_manager(dst)

        dbm_conf = DatabaseManagerConfig()
        dbm_conf.DATABASE_NAME = "test_dst_mulit_node_db"
        dbm_conf.COLLECTION_NAME = "test_dst_mulit_node_collection_" + str(i)
        dbm = DatabaseManager(dbm_conf)

        if i > 0:
            dbms.append(dbm)
        else:
            dbms.append(dbm)
            main_db = dbm

        cc.add_manager(dbm)

        cc_conf.RUN_FUNCTION = dst.run_main

        t = threading.Thread(target=run_node, args=(cc,))
        t.setDaemon(True)
        threads.append(t)

    start = None
    num_messages = 500
    try:

        print("Cleaning previous test data")
        for db in dbms:
            db.collection.delete_many({'imsi': '12345'})

        print("Initial state (before operations):")
        for dbm in dbms:
            count = dbm.collection.count()
            print(" total:", count)
        print()

        print("Starting nodes")
        for t in threads:
            t.start()

        time.sleep(1)

        print("Beginning test in 3 seconds")
        time.sleep(3)


        total_inserts = 0
        i = 0
        start = time.time()
        duration = 5
        for i in range(num_messages):
            # Do insert num_messages times at a rate of ~50/s
            main_db.database_insert("test_key_{0}".format(i), {"imsi": "12345"})
            i += 1
            total_inserts += 1
            time.sleep(0.02)

            if i % 100 == 99:
                time_passed = time.time() - start

                # check the current status of the other dbs
                print("Current state (during operations):")
                for dbm in dbms:
                    count = dbm.collection.count()
                    print(" total:", count, "rate: {0:.3f}".format(count/time_passed))
                print()

        print("operations finished")

        done = False
        while not done:
            done = True
            time.sleep(2)
            time_passed = time.time() - start

            # check the current status of the other dbs
            print("Current state (after operations), ctrl-c to skip:")
            for dbm in dbms:
                count = dbm.collection.count()
                done &= count >= num_messages
                print(" total:", count, "rate: {0:.3f}".format(count/time_passed))
            print()

        print("Total completion time:", time.time() - start)
        print("Test over, ctrl-c to clean up")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(" Stopping managers and cleaning up collections...")
        for cc in ccs:
            cc.stop()

        for db in dbms:
            db.collection.delete_many({'imsi': '12345'})

        print(" All test data deleted, ctrl-c to end")


def run_test():
    # single_node_test()
    multi_node_test()