from dAuth.tests import manager_tests
from dAuth.config import CCellularConfig

# Main file for running tests
# TODO: Add unittest


def run_manager_tests():
    config = CCellularConfig()
    config.OUTPUT_DIR = "./output/multi_node_test"
    manager_tests.run_multi_node_test(config, num_nodes=5)

def main():
    run_manager_tests()

if __name__ == "__main__":
    main()