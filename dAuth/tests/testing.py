from dAuth.tests import test_database, test_distributed


def main():
    test_database.run_tests()
    # test_distributed.run_test()
    

if __name__ == "__main__":
    main()