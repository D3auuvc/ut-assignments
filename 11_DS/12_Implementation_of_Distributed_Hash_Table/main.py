import sys
import time
import bisect
from node import Node


def start(file):
    
    with open(file, 'r') as f:
        print("Loading the initial ring from " + file + "...")
        lines = f.readlines()

    nextIsKeySpace = nextIsNodes = nextIsShortcuts = 0

    minKeySpace = maxKeySpace = 0
    nodes = []
    sockets = []
    count = 0
    port = 8001
    
    # Strips the newline character
    for line in lines:
        count += 1
        # min-max key values
        if nextIsKeySpace:
            minKeySpace = int(line.split(", ")[0])
            maxKeySpace = int(line.split(", ")[1])
            nextIsKeySpace = 0
        elif nextIsNodes:
            nodes = line.strip().split(", ")
            nodes.sort(key=int)
            nodesInt = []
            for node in nodes:
                node = int(node)
                if not check_key(node, minKeySpace, maxKeySpace):
                    continue
                nodesInt.append(node)

            nodes = nodesInt

            for node in nodes:
                socket = Node(port, node)
                port += 1
                socket.start()
                sockets.append(socket)

            enumeratedNodes = enumerate(nodes)
            for i, node in enumeratedNodes:
                connect_nodes(nodes, sockets, i)
            nextIsNodes = 0

        elif nextIsShortcuts:
            shortcuts = line.strip().split(", ")
            for shortcut in shortcuts:
                from_node, to_node = shortcut.split(':')
                sockets[nodes.index(int(from_node))].connect_with_shortcut(
                    sockets[nodes.index(int(to_node))].port)
            nextIsShortcuts = 0

        if line.strip() == "#key-space":
            nextIsKeySpace = 1
        elif line.strip() == "#nodes":
            nextIsNodes = 1
        elif line.strip() == "#shortcuts":
            nextIsShortcuts = 1

    sockets = sorted(sockets, key=lambda node: node.id)
    print("Initial ring loaded.")

    waitCommand = 1
    while waitCommand:
        command = input('Enter command(Exit command to quit):').lower()
        if command == "list":
            #: List the nodes in the ring (sorted from lower to higher). It also shows the references that
            # each node is storing. (: Shortcuts, S: successor, NS: next successor)
            for node in sorted(sockets, key=lambda node: node.id):
                print(str(node.id) + ":" + ",".join(str(x.id) for x in node.shortcuts) + ", S-" + str(
                    node.successor.id) + ", NS-" + str(node.next_successor))
        elif "shortcut" in command:
            from_node, to_node = command.split(' ')[1].split(':')
            sockets[nodes.index(int(from_node))].connect_with_shortcut(
                sockets[nodes.index(int(to_node))].port)
        elif "join" in command:
            join_node = int(command.split(' ')[1])
            if check_key(join_node, minKeySpace, maxKeySpace):
                bisect.insort(nodes, join_node)
                join_socket = Node(port, join_node)
                port += 1
                join_socket.start()
                index = nodes.index(join_node)
                sockets.insert(index, join_socket)
                connect_nodes(nodes, sockets, index)
                nextIsNodes = 0
        elif "exit" == command:
            print("Program exit.")
            sys.exit()
        else:
            print("Command not recognized, please try again.")

        time.sleep(0.1)


def usage():
    print("Usage:")
    print("filename")
    sys.exit(1)


def check_key(node, minKey, maxKey):
    if node > maxKey or minKey > node:
        print("Key %d is outside key space (%d, %d), skipping." %
              (node, minKey, maxKey))
        return False
    return True


def connect_nodes(nodes, sockets, index):
    if len(nodes) > index + 1:
        successorNumber = index + 1
    else:
        successorNumber = 0

    if len(nodes) > successorNumber + 1:
        nextSuccessor = nodes[successorNumber + 1]
    else:
        nextSuccessor = nodes[0]
    sockets[index].next_successor = nextSuccessor
    if index == len(nodes) - 1:
        sockets[index].connect_with_successor(sockets[0].port)
    else:
        sockets[index].connect_with_successor(sockets[index + 1].port)


def check_node(nodes, node):
    if node not in nodes:
        print("Node %d not present!" % (node))
        return False
    return True


if len(sys.argv) != 2:
    usage()
else:
    start(sys.argv[1])
