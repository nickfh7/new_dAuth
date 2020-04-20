import signal
import sys
import threading

from dAuth.ccellular import CCellular
from dAuth.managers import NetworkManager, TestManager
from network.services import LoggingClient

def main():
    print("Starting dAuth")
    print(" Creating CCellular")
    # Create the central manager
    cc = CCellular()

    # Add the network manager
    print("  Adding Network Manager")
    nwm = NetworkManager()
    # Grab the logging function
    cc.logger = nwm.get_service(LoggingClient.name).log
    cc.add_manager(nwm)

    # Add test manager for debugging
    print("  Adding Test Manager")
    tm = TestManager()
    cc.add_manager(tm)

    # Start running CCellular
    print(" Starting CCellular")
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