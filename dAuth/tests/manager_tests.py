from dAuth.ccellular import CCellular
from dAuth.managers.test_manager import TestManager

def simple_manager_test():
    print("Running simple manager test")
    c = CCellular()
    t = TestManager()
    c.add_manager(t)
    t.info()
    c.start()
    t.info()
    c.stop()
    t.info()

def multiple_manager_test():
    print("Running simple manager test")
    c = CCellular()

    t = TestManager()
    c.add_manager(t)
    t.info()

    t2 = TestManager(name="Test Manager 2")
    c.add_manager(t2)
    t2.info()

    c.start()

    t.info()
    t2.info()

    c.stop()
    t.info()
    t2.info()