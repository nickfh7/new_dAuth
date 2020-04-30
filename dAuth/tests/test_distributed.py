import time

from dAuth.ccellular import CCellular
from dAuth.managers import DistributedManager
from dAuth.config import DistributedManagerConfig, CCellularConfig

def single_node_test():
    cc_conf = CCellularConfig()
    cc_conf.OUTPUT_DIR = "./output/tests/distributed/single_node"
    cc = CCellular(cc_conf)

    dst_conf = DistributedManagerConfig()
    dst = DistributedManager(dst_conf)

    cc_conf.RUN_FUNCTION = dst.run_main()
    
    print("Starting")
    cc.start()
    print("Stopping")
    cc.stop()
    print("Stopped")


def run_test():
    single_node_test()