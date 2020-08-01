import time
import threading
import sys

from dAuth.proto.database_entry import DatabaseEntry
from dAuth.central_manager import CentralManager

num_inserts = 200
use_old_format = True

data = '{"_id": {"$oid": "5f06c13982e2ceefbc6edf1f"}, "imsi": "1234567890000", "ak": "90067853 E8E2", "amf": "", "autn": "90067853 A7608000 0DD7E6E1 6C269848", "ck": "05ABC825 BECE744D 776425AF D8141C43", "ik": "EAE625B0 15306BB8 243398FC AB92B660", "kasme": "40A88F3F C67D4111 F64FCBFF 15B08497 51E23254 0E6CF804 87658CC1 2EF4AC71", "rand": "7144BFD6 9778F74D E505D589 E7B87878", "sqn": "1122334455667788990011223344556677889900112233445566778899001122", "xres": "140F7A70 B7072208"}'
hex_obj = data.encode().hex()

def run_performance_tests(cm_list:list):
    main = cm_list[0]
    results = {}.fromkeys(range(5), 0)
    active_set = set(cm_list.copy())

    print("Message size (bytes):", sys.getsizeof(build_database_entry(0).get_serialized_message()))

    for cm in cm_list:
        threading.Thread(target=cm.start, daemon=True).start()

    start = time.time()
    for i in range(num_inserts):
        main.database_manager.update_entry(build_database_entry(i))
    
    print("Initial insert time:", time.time() - start)

    print_delay = 1
    ptime = time.time()
    while not all(results.values()):
        for cm in cm_list:
            if cm in active_set:
                count = cm.database_manager.count()
                if count >= num_inserts:
                    results[cm_list.index(cm)] = time.time() - start
                    active_set.remove(cm)

        if time.time() - ptime > print_delay:
            for cm in cm_list:
                count = cm.database_manager.count()
                print("DB {}: {} inserts".format(cm_list.index(cm), count))
                ptime = time.time()
            print()

        time.sleep(0.1)
    
    return results

def build_database_entry(imsi:int) -> DatabaseEntry:
    if use_old_format:
        return DatabaseEntry({
            "imsi": "1234567890" + str(imsi),
            "rand" : hex_obj,
            "sqn" : "1"
        })
    else:
        return DatabaseEntry({
            "imsi": "1234567890" + str(imsi),
            "rand" : "7144BFD6 9778F74D E505D589 E7B87878",
            "sqn" : "1122334455667788990011223344556677889900112233445566778899001122",
            "xres" : "140F7A70 B7072208",
            "kasme" : "40A88F3F C67D4111 F64FCBFF 15B08497 51E23254 0E6CF804 87658CC1 2EF4AC71",
            "autn" : "90067853 A7608000 0DD7E6E1 6C269848",
            "ck" : "05ABC825 BECE744D 776425AF D8141C43",
            "ak" : "90067853 E8E2",
            "ik" : "EAE625B0 15306BB8 243398FC AB92B660"
        })
