import sys
import re
import os
import glob
import operator


# Class for managing the logged data
class ExpData:
    message_types = ["Update", "Outbound", "Request", "Response", "Arrival", "Confirmation", "Merkle", "State_Delta"]
    other_types = ["Trigger", "Block_Commit", "DB_Commit", "NW_Usage"]
    all_types = message_types + other_types

    def __init__(self, data:str):
        self.ts = None  # Timestamp
        self.id = 0  # Identifier, i.e. of transaction
        self.node = None  # The node that the logging occured on
        self.type = None  # Type of log, i.e. 'Issuance'
        self.size = None  # Size of message (Message type only)
        self.mongo_ts = None  # Mongo timestamp (Trigger type only)

        # Network usage info
        self.tx = None
        self.rx = None
        self.interface = None

        self.valid = False

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
            self.mongo_ts = int(match[2]) * 1000
            self.ts = float(match[3])

        elif self.type == "Block_Commit":
            match = re.search(r"<EXP:[a-zA-Z0-9_:]+> ([a-zA-Z0-9_]+)-([0-9.]+)s", data)
            if (match == None):
                print("Message data invalid:", data)
                return
            self.id = match[1]
            self.ts = float(match[2])

        elif self.type == "DB_Commit":
            match = re.search(r"<EXP:[a-zA-Z0-9_:]+> ([a-zA-Z0-9_]+)-([0-9]+)-([0-9.]+)s", data)
            if (match == None):
                print("Message data invalid:", data)
                return
            self.id = match[1]
            self.mongo_ts = int(match[2]) * 1000
            self.ts = float(match[3])

        elif self.type == "NW_Usage":
            match = re.search(r"<EXP:[a-zA-Z0-9_:]+> ([a-zA-Z0-9\-_]+):([a-zA-Z0-9_]+)rx-([0-9]+)tx-([0-9.]+)s", data)
            if (match == None):
                print("Message data invalid:", data)
                return
            self.interface = match[1]
            self.rx = int(match[2])
            self.tx = int(match[3])
            self.ts = float(match[4])

        else:
            print("Unused type:", self.type)
            return


        self.ts = int(self.ts*1000)
        self.valid = True

    def entry_str(self) -> str:
        if self.type in self.message_types:
            return str(self.type) + " "*(14 - len(self.type))\
                   + str(self.node) + " "*(12 - len(self.node))\
                   + str(self.ts) + " "*(16 - len(str(self.ts)))\
                   + str(self.size)
        elif self.type == "Trigger" or self.type == "DB_Commit":
            return str(self.type) + " "*(14 - len(self.type))\
                   + str(self.node) + " "*(12 - len(self.node))\
                   + str(self.ts) + " "*(16 - len(str(self.ts)))\
                   + str(self.mongo_ts)
        else:
            return "INVALID"

    def node_str(self) -> str:
        if self.type in self.message_types:
            return str(self.type) + " "*(14 - len(self.type))\
                   + str(self.id) + " "*(18 - len(self.id))\
                   + str(self.ts) + " "*(16 - len(str(self.ts)))\
                   + str(self.size)
        elif self.type == "Trigger" or self.type == "DB_Commit":
            return str(self.type) + " "*(14 - len(self.type))\
                   + str(self.id) + " "*(26 - len(self.id))\
                   + str(self.ts) + " "*(16 - len(str(self.ts)))\
                   + str(self.mongo_ts)
        elif self.type == "Block_Commit":
            return str(self.type) + " "*(14 - len(self.type))\
                   + str(self.id)[0:16] + " "*(2)\
                   + str(self.ts) + " "*(16 - len(str(self.ts)))
        else:
            return "INVALID"


# Class for managing all of the results
class ExpResults:
    def __init__(self):
        self.entries = []
        self.entry_messages = {}
        self.node_messages = {}
        self.node_triggers = {}
        self.nw_usages = {}
        self.entry_types = dict.fromkeys(ExpData.all_types, 0)
        self.nodes = set()

    def add_entries(self, entries:list):
        for entry in entries:
            if entry.valid:
                self.add_entry(entry)

    def add_entry(self, entry:ExpData):
        if entry.type in ExpData.all_types:
            self.nodes.add(entry.node)
            self.entry_types[entry.type] += 1

        if entry.type in ExpData.message_types or entry.type == "DB_Commit":
            if entry.id not in self.entry_messages:
                self.entry_messages[entry.id] = []
            self.entry_messages[entry.id].append(entry)
            self.entry_messages[entry.id].sort(key=operator.attrgetter("ts"))

        if entry.type in ExpData.message_types or entry.type == "Block_Commit":
            if entry.node not in self.node_messages:
                self.node_messages[entry.node] = []
            self.node_messages[entry.node].append(entry)
            self.node_messages[entry.node].sort(key=operator.attrgetter("ts"))

        if entry.type == "Trigger":
            if entry.node not in self.node_triggers:
                self.node_triggers[entry.node] = []
            self.node_triggers[entry.node].append(entry)
            self.node_triggers[entry.node].sort(key=operator.attrgetter("ts"))

        if entry.type == "NW_Usage":
            if entry.node not in self.nw_usages:
                self.nw_usages[entry.node] = {}

            if entry.interface not in self.nw_usages[entry.node]:
                self.nw_usages[entry.node][entry.interface] = []
            
            self.nw_usages[entry.node][entry.interface].append(entry)
            self.nw_usages[entry.node][entry.interface].sort(key=operator.attrgetter("ts"))


    # Creates a list of strings representing lines of output
    def get_results(self) -> dict:
        results = {}
        output = []
        
        # Collect timestamp sorted trace of all messages
        insert_to_block_commit_delay = []
        output = []
        results["traces"] = {}
        traces = results["traces"]
        for entry_id, entry_list in self.entry_messages.items():
            traces[entry_id] = output

            # Data about trace
            start = None
            end = None
            for entry in entry_list:  # Sorted
                if not start:
                    if entry.type == "DB_Commit":
                        start = entry
                elif not end:
                    if entry.type == "State_Delta":
                        end = entry
                else:
                    break

            if start is not None and end is not None:
                delay = end.ts - start.ts
                insert_to_block_commit_delay.append(delay)
                output.append("Delay from commit to insert: {}ms".format(str(delay)))
                output.append("")

            # Actual trace
            output.append("Trace:")
            output.append("<type>        <node>      <timestamp ms>  <size or other>")
            for entry in entry_list:
                output.append("{}".format(entry.entry_str()))
            output = []

        # Collect timestamp sorted history of all messages on each node
        output = []
        results["nodes"] = {}
        nodes = results["nodes"]
        for entry_id, entry_list in self.node_messages.items():
            nodes[entry_id] = output
            output.append("<type>        <id>              <timestamp ms>  <size or other>")
            for entry in entry_list:
                output.append("{}".format(entry.node_str()))
            output = []

        # Collect timestamp sorted history of all triggers on each node
        output = []
        results["triggers"] = {}
        triggers = results["triggers"]
        for entry_id, entry_list in self.node_triggers.items():
            triggers[entry_id] = output
            output.append("<type>        <mongo id>                <timestamp ms>  <mongo ts>")
            for entry in entry_list:
                output.append("{}".format(entry.node_str()))
            output = []
        
        # Collect metadate about logging (how many of each type)
        results["summary"] = output
        output.append("Summary:")
        output.append("  Number of nodes: " + str(len(self.nodes)))
        output.append("  Number of unique entries: " + str(len(self.entry_messages)))
        output.append("  Avg delay insert to block commit: {}ms".format(str(sum(insert_to_block_commit_delay) // len(insert_to_block_commit_delay))))
        output.append("   * Affected by both sync rate and batch rate, check config")
        output.append("  Entries by type:")
        for k, v in self.entry_types.items():
            output.append("    {} {}{}".format(v, " "*(4-len(str(v))), k))

        # Collect network usage history
        results["nw_usage"] = {}
        nodes = results["nw_usage"]
        for node, interfaces in self.nw_usages.items():
            for interface, entries in interfaces.items():
                if len(entries) < 2:
                    continue

                if node not in nodes:
                    nodes[node] = {}
                nodes[node][interface] = output

                rx_snaps = [e.rx for e in entries]
                tx_snaps = [e.tx for e in entries]
                ts_snaps = [e.ts for e in entries]

                avg_rx = (rx_snaps[-1] - rx_snaps[0]) // (len(entries) - 1)
                avg_tx = (tx_snaps[-1] - tx_snaps[0]) // (len(entries) - 1)
                avg_ts = (ts_snaps[-1] - ts_snaps[0]) // (len(entries) - 1)

                output.append("Measure rate: {} s".format(avg_ts / 1000))
                output.append("Average rx rate: {} B/s".format(avg_rx/avg_ts*1000))
                output.append("Average tx rate: {} B/s".format(avg_tx/avg_ts*1000))
                output.append("")

                output.append("All rx measurements:")
                output.append("<Bytes since last>  <timestamp ms>")
                le = entries[0]
                for entry in entries[1:]:
                    val = str(entry.rx - le.rx)
                    output.append("{}{}  {}".format(val, " "*(len("<Bytes since last>") - len(val)), entry.ts))
                    le = entry

                output = []

        return results

    def output_results(self, output_dir:str):
        results = self.get_results()
        self._output_results(output_dir, results)

    def _output_results(self, output_dir:str, results:dict):
        os.makedirs(output_dir, exist_ok=True)
        for name in results.keys():
            path = os.path.join(output_dir, name)
            content = results[name]
            if type(content) is dict:
                self._output_results(path, content)
            elif type(content) is list:
                with open(path, 'w') as f:
                    f.writelines([e + '\n' for e in content])
            else:
                print("Bad result type:", str(content))


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
                    entry = ExpData(line)
                    if entry.valid:
                        entries.append(entry)
    
    return entries


# Processes the entries stored withing any files under the provided logfile directory
def process_results(logfile_dir:str, output_file:str=None) -> ExpResults:
    results = ExpResults()
    results.add_entries(parse_files_for_entries(logfile_dir))
    return results


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: exp_results logfile_dir output_dir")
        exit(1)

    results = process_results(sys.argv[1])
    results.output_results(sys.argv[2])
