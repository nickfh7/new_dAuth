import time
import threading

from dAuth.config import DistributedManagerConfig
from dAuth.managers import DistributedManager
from dAuth.proto.database_entry import DatabaseEntry

# Tests that triggers are functioning

def trigger_test():
    print("Running trigger tests")

    trigger_map = {}

    def update_trigger_map(key):
        if key not in trigger_map:
            trigger_map[key] = 1

    conf = DistributedManagerConfig()
    conf.BATCH_TIMEOUT = 0.5
    conf.BATCH_SIZE = 20
    manager = DistributedManager(conf)
    manager.set_report_callback(update_trigger_map)

    # Start triggers
    manager.start()
    threading.Thread(target=manager.run_main, daemon=True).start()

    try:
        print(" Testing single trigger single key")
        manager.update_entry(DatabaseEntry({'imsi': '1', 'sqn':'0'}))
        time.sleep(2)
        assert trigger_map == {'1': 1}

        trigger_map.clear()

        print(" Testing multiple trigger single key")
        manager.update_entry(DatabaseEntry({'imsi': '1', 'sqn':'1'}))
        manager.update_entry(DatabaseEntry({'imsi': '1', 'sqn':'2'}))
        manager.update_entry(DatabaseEntry({'imsi': '1', 'sqn':'3'}))
        manager.update_entry(DatabaseEntry({'imsi': '1', 'sqn':'4'}))
        manager.update_entry(DatabaseEntry({'imsi': '1', 'sqn':'5'}))
        time.sleep(2)
        print(trigger_map)
        assert trigger_map == {'1': 1}

        trigger_map.clear()

        print(" Testing single trigger multiple key")
        manager.update_entry(DatabaseEntry({'imsi': '1', 'sqn':'1'}))
        manager.update_entry(DatabaseEntry({'imsi': '2', 'sqn':'2'}))
        manager.update_entry(DatabaseEntry({'imsi': '3', 'sqn':'3'}))
        manager.update_entry(DatabaseEntry({'imsi': '4', 'sqn':'4'}))
        manager.update_entry(DatabaseEntry({'imsi': '5', 'sqn':'5'}))
        time.sleep(2)
        assert trigger_map == {'1': 1, '2': 1, '3': 1, '4': 1, '5': 1}

        trigger_map.clear()

        print(" Testing multiple trigger multiple key")
        manager.update_entry(DatabaseEntry({'imsi': '1', 'sqn':'01'}))
        manager.update_entry(DatabaseEntry({'imsi': '2', 'sqn':'02'}))
        manager.update_entry(DatabaseEntry({'imsi': '3', 'sqn':'03'}))
        manager.update_entry(DatabaseEntry({'imsi': '4', 'sqn':'04'}))
        manager.update_entry(DatabaseEntry({'imsi': '5', 'sqn':'05'}))
        manager.update_entry(DatabaseEntry({'imsi': '1', 'sqn':'11'}))
        manager.update_entry(DatabaseEntry({'imsi': '2', 'sqn':'12'}))
        manager.update_entry(DatabaseEntry({'imsi': '3', 'sqn':'13'}))
        manager.update_entry(DatabaseEntry({'imsi': '4', 'sqn':'14'}))
        manager.update_entry(DatabaseEntry({'imsi': '5', 'sqn':'15'}))
        manager.update_entry(DatabaseEntry({'imsi': '1', 'sqn':'21'}))
        manager.update_entry(DatabaseEntry({'imsi': '2', 'sqn':'22'}))
        manager.update_entry(DatabaseEntry({'imsi': '3', 'sqn':'23'}))
        manager.update_entry(DatabaseEntry({'imsi': '4', 'sqn':'24'}))
        manager.update_entry(DatabaseEntry({'imsi': '5', 'sqn':'25'}))
        time.sleep(2)
        assert trigger_map == {'1': 1, '2': 1, '3': 1, '4': 1, '5': 1}

        manager.stop()

    except AssertionError as e:
        manager.stop()
        print("Test Failed:", e)
        return

    print("Test Success")

def run_tests():
    try:
        trigger_test()
    except Exception as e:
        print("Test Failed:", e)

if __name__ == "__main__":
    run_tests()