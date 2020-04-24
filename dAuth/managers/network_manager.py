from dAuth.managers.interface import ManagerInterface
from dAuth.config import NetworkManagerConfig
from network import NetworkManager, services

class NetworkManagerWrapper(ManagerInterface):
    name = "Network Manager"

    def __init__(self, conf:NetworkManagerConfig):
        super().__init__(conf)

        # Build network manager
        self._network_manager = NetworkManager(port=conf.GRPC_PORT,
                                               known_priorities=conf.PRIORITIES,
                                               limit_to_known_priorities=conf.LIMIT_PRIORITIES,
                                               logfile_dir=conf.OUTPUT_DIR,)

        # Add network services
        self._network_manager.add_service(services.DebugPing())
        self._network_manager.add_service(services.LoggingClient(host=conf.LOGGING_SERVER_HOST,
                                                                 port=conf.LOGGING_SERVER_PORT,))

    def get_service(self, service_name):
        return self._network_manager.get_service(service_name)

    def _start(self):
        self._network_manager.start()

    def _stop(self):
        self._network_manager.stop()