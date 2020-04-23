import argparse

from dAuth.config import CCellularConfig,\
                         NetworkManagerConfig,\
                         DatabaseManagerConfig,\
                         DistributedManagerConfig


def parse_args(cc_config:CCellularConfig=None, 
               nwm_config:NetworkManagerConfig=None,
               dbm_config:DatabaseManagerConfig=None,
               dstm_config:DistributedManagerConfig=None):

    # Build parser and add arguments for each available config
    parser = argparse.ArgumentParser(description="dAuth arguments are prefixed by shorthand manager type, i.e. --cc- or --db-")

    # CCellular
    if cc_config:
        parser.add_argument("--cc-id", help="specify an id (randomly generated otherwise)", default=cc_config.ID)
        parser.add_argument("--cc-out", help="directory for output, i.e. logs", default=cc_config.OUTPUT_DIR)

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
        pass

    args = parser.parse_args()

    # Add results to each config
    # CCellular
    if cc_config:
        cc_config.ID = args.cc_id
        cc_config.OUTPUT_DIR = args.cc_out

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
        pass
