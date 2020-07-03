import time

from dAuth.config import DatabaseManagerConfig
from dAuth.managers import DatabaseManager
from dAuth.proto.database_entry import DatabaseEntry

def insert_test():
    conf = DatabaseManagerConfig()
    conf.COLLECTION_NAME = "simple_insert_collection"
    manager = DatabaseManager(conf)
    manager.collection.drop()
    manager.logger = print

    manager.update_entry(DatabaseEntry({'imsi': '1', 'rand':'01'}))

    time.sleep(1)

    print("CHECKING:", manager.get_entry('1').to_dict())
    manager.update_entry(DatabaseEntry({'imsi': '1', 'rand':'02'}))

    time.sleep(1)

    print("CHECKING:", manager.get_entry('1').to_dict())


if __name__ == "__main__":
    insert_test()