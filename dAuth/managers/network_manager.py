from dAuth.managers.interface import ManagerInterface
from network import NetworkManager, services

class NetworkManagerWrapper(ManagerInterface):
    name = "Network Manager"

    def __init__(self):
        # Build network manager
        self._network_manager = NetworkManager()

        # Add network services
        self._network_manager.add_service(services.DebugPing())
        self._network_manager.add_service(services.LoggingClient())

    def get_service(self, service_name):
        return self._network_manager.get_service(service_name)

    def start(self):
        self._network_manager.start()

    def stop(self):
        self._network_manager.stop()