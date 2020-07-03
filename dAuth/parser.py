import argparse

from dAuth.config import CentralManagerConfig,\
                         NetworkManagerConfig,\
                         DatabaseManagerConfig,\
                         DistributedManagerConfig,\
                         SyncManagerConfig


def parse_args(cm_config:CentralManagerConfig=None, 
               nwm_config:NetworkManagerConfig=None,
               dbm_config:DatabaseManagerConfig=None,
               dstm_config:DistributedManagerConfig=None,
               sync_config:SyncManagerConfig=None):

    # Build parser and add arguments for each available config
    parser = argparse.ArgumentParser(description="dAuth arguments are prefixed by shorthand manager type, i.e. --cc- or --db-")

    # Central manager
    if cm_config:
        parser.add_argument("--cc-id", help="specify an id (randomly generated otherwise)", default=cm_config.ID)
        parser.add_argument("--cc-out", help="directory for output, i.e. logs", default=cm_config.OUTPUT_DIR)

    # Network manager
    if nwm_config:
        parser.add_argument("--nwm-out", help="directory for output, i.e. logs", default=nwm_config.OUTPUT_DIR)
        parser.add_argument("--nwm-port", help="port to run gRPC server on", default=nwm_config.GRPC_PORT)
        parser.add_argument("--nwm-log-host", help="host of the logging server", default=nwm_config.LOGGING_SERVER_HOST)
        parser.add_argument("--nwm-log-port", help="port of the logging server", default=nwm_config.LOGGING_SERVER_PORT)

    # Database manager
    if dbm_config:
        parser.add_argument("--db-host", help="host for the Mongo db", default=dbm_config.HOST)
        parser.add_argument("--db-port", help="port for the Mongo db", default=dbm_config.PORT)
        parser.add_argument("--db-name", help="name of the database", default=dbm_config.DATABASE_NAME)
        parser.add_argument("--db-collection", help="name of collection within database", default=dbm_config.COLLECTION_NAME)

    # Distributed manager
    if dstm_config:
        parser.add_argument("--dst-validator-url", help="url of validator to send transactions", default=dstm_config.VALIDATOR_URL)
        parser.add_argument("--dst-client-key-path", help="local key path for the client", default=dstm_config.CLIENT_KEY_PATH)
        parser.add_argument("--dst-client-url", help="client url of the sawtooth node", default=dstm_config.CLIENT_URL)
        parser.add_argument("--dst-batch-size", help="max size of transaction batches", default=dstm_config.BATCH_SIZE)
        parser.add_argument("--dst-batch-timeout", help="timeout before sending available batch", default=dstm_config.BATCH_TIMEOUT)
        parser.add_argument("--dst-batch-check-delay", help="time between checking for new transactions", default=dstm_config.BATCH_CHECK_DELAY)

    args = parser.parse_args()

    # Add results to each config
    # Central Manager
    if cm_config:
        cm_config.ID = args.cc_id
        cm_config.OUTPUT_DIR = args.cc_out

    # Network manager
    if nwm_config:
        nwm_config.OUTPUT_DIR = args.nwm_out
        nwm_config.GRPC_PORT = args.nwm_port
        nwm_config.LOGGING_SERVER_HOST = args.nwm_log_host
        nwm_config.LOGGING_SERVER_PORT = args.nwm_log_port

    # Database manager
    if dbm_config:
        dbm_config.HOST = args.db_host
        dbm_config.PORT = args.db_port
        dbm_config.DATABASE_NAME = args.db_name
        dbm_config.COLLECTION_NAME = args.db_collection

    # Distributed manager
    if dstm_config:
        dstm_config.VALIDATOR_URL = args.dst_validator_url
        dstm_config.CLIENT_KEY_PATH = args.dst_client_key_path
        dstm_config.CLIENT_URL = args.dst_client_url
        dstm_config.BATCH_SIZE = args.dst_batch_size
        dstm_config.BATCH_TIMEOUT = args.dst_batch_timeout
        dstm_config.BATCH_CHECK_DELAY = args.dst_batch_check_delay
