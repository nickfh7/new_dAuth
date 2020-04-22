from dAuth.managers.interface import ManagerInterface
from network import NetworkManager, services

class NetworkManagerWrapper(ManagerInterface):
    name = "Network Manager"

    def __init__(self, config, name=None):
        super().__init__(config, name=name)

        # Build network manager
        self._network_manager = NetworkManager(port=config.GRPC_PORT,
                                               known_priorities=config.PRIORITIES,
                                               limit_to_known_priorities=config.LIMIT_PRIORITIES,
                                               logfile_dir=config.OUTPUT_DIR,)

        # Add network services
        self._network_manager.add_service(services.DebugPing())
        self._network_manager.add_service(services.LoggingClient(host=config.LOGGING_SERVER_HOST,
                                                                 port=config.LOGGING_SERVER_PORT,))

    def get_service(self, service_name):
        return self._network_manager.get_service(service_name)

    def _start(self):
        self._network_manager.start()

    def _stop(self):
        self._network_manager.stop()