import sys
import re
import os
import glob
import operator

class ExpData:
    message_types = ["Issuance", "Outbound", "Request", "Response", "Arrival", "Confirmation"]
    other_types = ["Trigger"]
    all_types = message_types + other_types

    def __init__(self, data:str):
        self.ts = None  # Timestamp
        self.id = None  # Identifier, i.e. of transaction
        self.node = None  # The node that the logging occured on
        self.type = None  # Type of log, i.e. 'Issuance'
        self.size = None  # Size of message (Message type only)
        self.mongo_ts = None  # Mongo timestamp (Trigger type only)

        # get type from data
        match = re.search(r"<EXP:([a-zA-Z0-9_]+):([a-zA-Z0-9_]+)>", data)
        if (match == None):
            print("Invalid data:", data)
            return
        self.node = match[1]  # Node that the data occured on
        self.type = match[2]
        if (self.type not in self.all_types):
            print("Invalid type:", self.type)
            return

        if self.type in self.message_types:
            match = re.search(r"<EXP:[a-zA-Z0-9_:]+> ([a-zA-Z0-9_]+)-([0-9]+)B-([0-9.]+)s", data)
            if (match == None):
                print("Message data invalid:", data)
                return
            self.id = match[1]
            self.size = int(match[2])
            self.ts = float(match[3])

        elif self.type == "Trigger":
            match = re.search(r"<EXP:[a-zA-Z0-9_:]+> ([a-zA-Z0-9_]+)-Timestamp\(([0-9]+), [0-9]+\)-([0-9.]+)", data)
            if (match == None):
                print("Message data invalid:", data)
                return
            self.id = match[1]
            self.mongo_ts = float(match[2])
            self.ts = float(match[3])

    def entry_str(self):
        if self.type in self.message_types:
            return str(self.type) + " "*(14 - len(self.type))\
                   + str(self.node) + " "*(12 - len(self.node))\
                   + str(self.ts) + " "*(20 - len(str(self.ts)))\
                   + str(self.size)
        elif self.type == "Trigger":
            return str(self.type) + " "*(13 - len(self.type))\
                   + str(self.node) + " "*(12 - len(self.node))\
                   + str(self.ts) + " "*(20 - len(str(self.ts)))\
                   + str(self.mongo_ts)
        else:
            return "INVALID"

    def node_str(self):
        if self.type in self.message_types:
            return str(self.type) + " "*(14 - len(self.type))\
                   + str(self.id) + " "*(12 - len(self.node))\
                   + str(self.ts) + " "*(20 - len(str(self.ts)))\
                   + str(self.size)
        elif self.type == "Trigger":
            return str(self.type) + " "*(13 - len(self.type))\
                   + str(self.id) + " "*(12 - len(self.node))\
                   + str(self.ts) + " "*(20 - len(str(self.ts)))\
                   + str(self.mongo_ts)
        else:
            return "INVALID"


# Returns a list of all files within a directory
def get_files(main_dir:str) -> list:
    paths = glob.glob(main_dir + '/**/*', recursive=True)
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)

    return files


def main(main_dir:str) -> None:
    # Grab all entries from all files in the directory (recursively)
    files = get_files(main_dir)
    entries = []
    for filename in files:
        with open(filename, 'r') as f:
            for line in f:
                if "EXP" in line:
                    entries.append(ExpData(line))

    # Collect metadate about logging (how many of each type)
    print("Entry metadata")
    node_set = set()
    for entry in entries:
        node_set.add(entry.node)
    print("  Number of nodes:", len(node_set))

    entry_messages = {}
    for entry in entries:
        if entry.type in ExpData.message_types:
            if entry.id not in entry_messages:
                entry_messages[entry.id] = []
            
            entry_messages[entry.id].append(entry)
    print("  Number of unique entries:", len(entry_messages))

    print("  Entries by type:")
    entry_types = dict.fromkeys(ExpData.all_types, 0)
    for entry in entries:
        entry_types[entry.type] += 1
    for k, v in entry_types.items():
        print("    {} {}{}".format(v, " "*(4-len(str(v))), k))
    print()
    
    print("Entry traces")
    for entry_list in entry_messages.values():
        entry_list.sort(key=operator.attrgetter("ts"))
    for entry_id, entry_list in entry_messages.items():
        print("  {}:".format(entry_id))
        for entry in entry_list:
            print("    {}".format(entry.entry_str()))
    print()

    print("Node history")
    node_messages = {}
    for entry in entries:
        if entry.type in ExpData.message_types:
            if entry.node not in node_messages:
                node_messages[entry.node] = []
            
            node_messages[entry.node].append(entry)
    for entry_list in node_messages.values():
        entry_list.sort(key=operator.attrgetter("ts"))
    for node, entry_list in node_messages.items():
        print("  {}:".format(node))
        for entry in entry_list:
            print("    {}".format(entry.node_str()))
    print()
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Input top level directory of nodes")
        exit(1)

    main(sys.argv[1])