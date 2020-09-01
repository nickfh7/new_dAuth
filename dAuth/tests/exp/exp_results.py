import sys
import re
import os
import glob
import operator

# TODO:
# - Add separate files for each results type


# Class for managing the logged data
class ExpData:
    message_types = ["Issuance", "Outbound", "Request", "Response", "Arrival", "Confirmation", "LocalDB"]
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

    def entry_str(self) -> str:
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

    def node_str(self) -> str:
        if self.type in self.message_types:
            return str(self.type) + " "*(14 - len(self.type))\
                   + str(self.id) + " "*(12 - len(self.node))\
                   + str(self.ts) + " "*(20 - len(str(self.ts)))\
                   + str(self.size)
        elif self.type == "Trigger":
            return str(self.id) + " "*(12 - len(self.node))\
                   + str(self.ts) + " "*(20 - len(str(self.ts)))\
                   + str(self.mongo_ts)
        else:
            return "INVALID"


# Class for managing all of the results
class ExpResults:
    def __init__(self):
        self.entries = []
        self.entry_messages = {}
        self.node_messages = {}
        self.node_triggers = {}
        self.entry_types = dict.fromkeys(ExpData.all_types, 0)
        self.nodes = set()

    def add_entries(self, entries:list):
        for entry in entries:
            self.add_entry(entry)

    def add_entry(self, entry:ExpData):
        if entry.type in ExpData.all_types:
            self.nodes.add(entry.node)
            self.entry_types[entry.type] += 1

        if entry.type in ExpData.message_types:
            if entry.id not in self.entry_messages:
                self.entry_messages[entry.id] = []
            self.entry_messages[entry.id].append(entry)
            self.entry_messages[entry.id].sort(key=operator.attrgetter("ts"))

            if entry.node not in self.node_messages:
                self.node_messages[entry.node] = []
            self.node_messages[entry.node].append(entry)
            self.node_messages[entry.node].sort(key=operator.attrgetter("ts"))

        elif entry.type == "Trigger":
            if entry.node not in self.node_triggers:
                self.node_triggers[entry.node] = []
            self.node_triggers[entry.node].append(entry)
            self.node_triggers[entry.node].sort(key=operator.attrgetter("ts"))

    # Creates a list of strings representing lines of output
    def get_results(self) -> list:
        output = []

        # Collect metadate about logging (how many of each type)
        output.append("Entry metadata")
        output.append("  Number of nodes: " + str(len(self.nodes)))
        output.append("  Number of unique entries: " + str(len(self.entry_messages)))
        output.append("  Entries by type:")
        for k, v in self.entry_types.items():
            output.append("    {} {}{}".format(v, " "*(4-len(str(v))), k))
        output.append("")
        output.append("")
        
        # Collect timestamp sorted trace of all messages
        output.append("Entry traces")
        output.append("  <id>:")
        output.append("    <type>        <node>      <timestamp>         <size>")
        output.append("")
        for entry_id, entry_list in self.entry_messages.items():
            output.append("  {}:".format(entry_id))
            for entry in entry_list:
                output.append("    {}".format(entry.entry_str()))
            output.append("")
        output.append("")

        # Collect timestamp sorted history of all messages on each node
        output.append("Node history")
        output.append("  <node>:")
        output.append("    <type>        <id>              <timestamp>         <size>")
        output.append("")
        for node, entry_list in self.node_messages.items():
            output.append("  {}:".format(node))
            for entry in entry_list:
                output.append("    {}".format(entry.node_str()))
            output.append("")
        output.append("")

        # Collect timestamp sorted history of all triggers on each node
        output.append("Node Triggers")
        output.append("  <node>:")
        output.append("    <mongo id>                <timestamp>         <mongo ts>")
        output.append("")
        for node, entry_list in self.node_triggers.items():
            output.append("  {}:".format(node))
            for entry in entry_list:
                output.append("    {}".format(entry.node_str()))
            output.append("")
        output.append("")

        return output

    def output_results_to_file(self, filename:str):
        with open(filename, 'w') as f:
            f.writelines([e + '\n' for e in self.get_results()])

    def output_results_to_console(self):
        for line in self.get_results():
            print(line)


# Returns a list of entries
def parse_files_for_entries(logfile_dir:str) -> list:
    # Get all files
    paths = glob.glob(logfile_dir + '/**/*', recursive=True)
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)

    # Grab all entries from files
    entries = []
    for filename in files:
        with open(filename, 'r') as f:
            for line in f:
                if "EXP" in line:
                    entries.append(ExpData(line))
    
    return entries


# Processes the entries stored withing any files under the provided logfile directory
def process_results(logfile_dir:str, output_file:str=None) -> ExpResults:
    results = ExpResults()
    results.add_entries(parse_files_for_entries(logfile_dir))
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: exp_results logfile_dir [output_file]")
        exit(1)

    results = process_results(sys.argv[1])

    if len(sys.argv) > 2:
        results.output_results_to_file(sys.argv[2])
    else:
        results.output_results_to_console()
