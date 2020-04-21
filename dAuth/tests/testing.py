from dAuth.tests import manager_tests
from dAuth.config import CCellularConfig

# Main file for running tests


def run_manager_tests():
    cc_conf = CCellularConfig()
    # manager_tests.run_all_simple_tests(cc_conf)
    # cc_conf.OUTPUT_DIR = "./output/full_setup"
    # manager_tests.run_full_setup(cc_conf)
    manager_tests.run_multi_node(cc_conf, num_nodes=5)

if __name__ == "__main__":
    run_manager_tests()