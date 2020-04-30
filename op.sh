# Example insert, update, and delete commands
# Emulates the op document format (without all the db details)
db-operation --op-type i '{"o": {"_id":"some_id_1", "imsi":"1", "security":{"op":"a"}}}'
db-operation --op-type u '{"o2": {"_id":"some_id_1"}, "o": {"$v": 1, "$set": {"imsi": "2", "security": {"op": "b"}}}}'
db-operation --op-type d '{"o": {"_id":"some_id_1"}}'
