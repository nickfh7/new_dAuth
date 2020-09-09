import threading
import time
import os

from dAuth.config import NetworkManagerConfig

class NetworkUsagePoll:
    def __init__(self, conf:NetworkManagerConfig, poll_callback):
        self.conf = conf
        self.running = False
        self.logger = None
        self.poll_callback = poll_callback

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.poller, daemon=True).start()

    def stop(self):
        if self.running:
            self.running = False

    def poller(self):
        self.log("Poller starting")
        last_poll_time = 0  # Always do initial
        while self.running:
            if time.time() - last_poll_time > self.conf.POLL_INTERVAL:
                self.log("  Getting data...")
                self.poll_callback(self.get_poll_data())
                last_poll_time = time.time()
            
            time.sleep(self.conf.POLL_CHECK_DELAY)
        
    def get_poll_data(self):
        try:
            poll_dir = "/sys/class/net/"
            results = {}
            for filename in os.listdir(poll_dir):
                cur_dir = os.path.join(poll_dir, filename, "statistics/")
                results[filename] = {}
                for name in ("rx_bytes", "tx_bytes"):
                    with open(os.path.join(cur_dir, name), 'r') as f:
                        val = int(f.readline())
                        results[filename][name] = val
        
            return results

        except Exception as e:
            self.log("Failed to get data: " + str(e))


    def log(self, message):
        if self.logger:
            self.logger("(Network Usage Poll) " + str(message))