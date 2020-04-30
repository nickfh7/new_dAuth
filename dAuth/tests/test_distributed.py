import time
import threading

from dAuth.ccellular import CCellular
from dAuth.managers import DistributedManager, DatabaseManager
from dAuth.config import DistributedManagerConfig, CCellularConfig, DatabaseManagerConfig

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


def multi_node_test():
    def run_node(cc_node):
        cc_node.start()
        cc_node.stop()

    threads = []

    for i in range(5):
        cc_conf = CCellularConfig()
        cc_conf.OUTPUT_DIR = "./output/tests/distributed/mulit_node_" + str(i)
        cc = CCellular(cc_conf)

        dst_conf = DistributedManagerConfig()
        dst_conf.VALIDATOR_URL = 'tcp://localhost:' + str(4004 + i)
        dst = DistributedManager(dst_conf)
        cc.add_manager(dst)

        dbm_conf = DatabaseManagerConfig()
        if i > 0:
            dbm_conf.DATABASE_NAME = "open5gs__" + str(i)
        dbm = DatabaseManager(dbm_conf)
        cc.add_manager(dbm)

        cc_conf.RUN_FUNCTION = dst.run_main

        t = threading.Thread(target=run_node, args=(cc,))
        t.setDaemon(True)
        threads.append(t)

    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test ending (may need a bunch of ctrl-c presses)")


def run_test():
    # single_node_test()
    multi_node_test()