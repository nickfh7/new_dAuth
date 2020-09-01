import sys
import signal
import threading

from network.services import LoggingServer
from network.network_manager import NetworkManager

# Runs a logging server to receive and record log messages

def run_server(port=14127):
    print('Starting Logging Server')
    nwm = NetworkManager(port=port)
    nwm.add_service(LoggingServer(consolidate_on_exit=False))
    nwm.start()

    def stop_server(signal, frame):
        print('\nStopping Logging Server')
        nwm.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop_server)
    print("Ctr-c to stop")
    forever = threading.Event()
    forever.wait()


# Boot up and wait for a keyboard interrupt
if __name__ == "__main__":
    run_server()