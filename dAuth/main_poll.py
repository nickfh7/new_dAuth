import threading
import time

from dAuth.central_manager import CentralManager
from dAuth.config import CentralManagerConfig,\
                         NetworkManagerConfig,\
                         DatabaseManagerConfig,\
                         DistributedManagerConfig,\
                         SyncManagerConfig
from dAuth.parser import parse_args
from dAuth.utils import random_string
from dAuth.proto.database_entry import DatabaseEntry


# Sets up a dAuth node to run indefinitely
# Periodically adds in a new message
def main():
    # Set up config objects and parsing
    cm_config = CentralManagerConfig()
    nwm_config = NetworkManagerConfig()
    dbm_config = DatabaseManagerConfig()
    dstm_config = DistributedManagerConfig()
    sync_config = SyncManagerConfig()
    parse_args(cm_config=cm_config, nwm_config=nwm_config, dbm_config=dbm_config, dstm_config=dstm_config)

    # Create the central manager
    cm = CentralManager(cm_config)
    cm.init_managers(dbm_config, dstm_config, sync_config, nwm_config)

    threading.Thread(target=cm.start, daemon=True).start()

    print("Starting transaction polling in 3 seconds")
    time.sleep(3)

    try:
        tps = 0.2
        rate = 1/tps
        start = time.time()

        while True:
            entry = DatabaseEntry({"imsi": random_string(15), 'max_known_sqn': "1", 
            "vectors": '[{\
                "rand" : "7144BFD6 9778F74D E505D589 E7B87878",\
                "sqn" :"1",\
				"xres" : "140F7A70 B7072208",\
				"kasme" : "40A88F3F C67D4111 F64FCBFF 15B08497 51E23254 0E6CF804 87658CC1 2EF4AC71",\
				"autn" : "90067853 A7608000 0DD7E6E1 6C269848",\
				"ck" : "05ABC825 BECE744D 776425AF D8141C43",\
				"ak" : "90067853 E8E2",\
				"ik" : "EAE625B0 15306BB8 243398FC AB92B660"\
                }]'})
            cm.database_manager.update_entry(entry)
            time.sleep(rate)

    except KeyboardInterrupt:
        pass



# Should not use this, use the installed command instead
if __name__ == "__main__":
    main()
