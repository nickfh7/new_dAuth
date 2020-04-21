import signal
import sys
import threading

from dAuth.ccellular import CCellular
from dAuth.managers import NetworkManager, TestManager, TestDatabaseManager, TestDistributedManager
from network.services import LoggingClient
from dAuth.config import CCellularConfig, NetworkManagerConfig, DatabaseManagerConfig, DistributedManagerConfig

def main():
    print("Starting dAuth")

    # Config
    cc_config = CCellularConfig()
    nwm_config = NetworkManagerConfig()
    dbm_config = DatabaseManagerConfig()
    dstm_config = DistributedManagerConfig()

    # Create the central manager
    cc = CCellular(cc_config)

    # Add the network manager
    nwm = NetworkManager(nwm_config)
    # Grab the logging function
    cc.logger = nwm.get_service(LoggingClient.name).log
    cc.add_manager(nwm)

    # Add test manager for debugging
    tm = TestManager()
    cc.add_manager(tm)

    # Add database manager
    dbm = TestDatabaseManager(dbm_config)
    cc.add_manager(dbm)

    # Add distributed manager
    dstm = TestDistributedManager(dstm_config)
    cc.add_manager(dstm)

    # Start running CCellular
    cc.start()

    # Create end function
    def stop_server(signal, frame):
        print('\nStopping...')
        cc.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop_server)
    print("Ctr-c to stop")
    forever = threading.Event()
    forever.wait()