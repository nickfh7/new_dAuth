import time

from dAuth.managers.interface import ManagerInterface
from dAuth.network.network_usage import NetworkUsagePoll
from dAuth.config import NetworkManagerConfig

from network import NetworkManager, services

class NetworkManagerWrapper(ManagerInterface):
    name = "Network Manager"

    def __init__(self, conf:NetworkManagerConfig):
        super().__init__(conf)

        # Build network manager
        self._network_manager = NetworkManager(port=conf.GRPC_PORT,
                                               host=conf.GRPC_HOST,
                                               known_priorities=conf.PRIORITIES,
                                               limit_to_known_priorities=conf.LIMIT_PRIORITIES,
                                               logfile_dir=conf.OUTPUT_DIR,)

        # Add network services
        # self._network_manager.add_service(services.DebugPing())
        self._network_manager.add_service(services.LoggingClient(host=conf.LOGGING_SERVER_HOST,
                                                                 port=conf.LOGGING_SERVER_PORT,))
        self._remote_log_func = self._network_manager.get_service("logging_client").log

        self._network_usage_poller = NetworkUsagePoll(self.conf, self._usage_poll)
        self._network_usage_poller.logger = self.log

    def _usage_poll(self, data:dict):
        if data is not None:
            for interface in data:
                rx = data[interface]["rx_bytes"]
                tx = data[interface]["tx_bytes"]
                self.log("<EXP:{}:NW_Usage> {}:{}rx-{}tx-{}s".format(self.conf.ID, interface, rx, tx, time.time()))

    def _remote_log(self, category, message):
        self._remote_log_func(category, message)

    def _start(self):
        self._network_manager.start()
        self._network_usage_poller.start()

    def _stop(self):
        self._network_manager.stop()
        self._network_usage_poller.stop()