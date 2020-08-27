from dAuth.managers import DatabaseManager
from dAuth.config import DatabaseManagerConfig
from dAuth.proto.database_entry import DatabaseEntry

conf  = DatabaseManagerConfig()
conf.COLLECTION_NAME = "test_extract"

dbm = DatabaseManager(conf)
dbm.collection.drop()
dbm.start()

def printout(message):
    from bson import json_util
    print(json_util.dumps(message['o']))
dbm.trigger_handler.triggers.register_insert_trigger(printout, db_name=dbm.trigger_handler.db_name, collection_name=dbm.trigger_handler.collection_name)


dbm.update_entry(DatabaseEntry({
    "imsi": "1234567890000",
    "rand" : "7144BFD6 9778F74D E505D589 E7B87878",
    "sqn" : "1122334455667788990011223344556677889900112233445566778899001122",
    "xres" : "140F7A70 B7072208",
    "kasme" : "40A88F3F C67D4111 F64FCBFF 15B08497 51E23254 0E6CF804 87658CC1 2EF4AC71",
    "autn" : "90067853 A7608000 0DD7E6E1 6C269848",
    "ck" : "05ABC825 BECE744D 776425AF D8141C43",
    "ak" : "90067853 E8E2",
    "ik" : "EAE625B0 15306BB8 243398FC AB92B660"
}))

import time
time.sleep(1)
dbm.stop()