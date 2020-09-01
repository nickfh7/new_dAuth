from dAuth.managers.interface import ManagerInterface
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

    def _remote_log(self, category, message):
        self._remote_log_func(category, message)

    def _start(self):
        self._network_manager.start()

    def _stop(self):
        self._network_manager.stop()