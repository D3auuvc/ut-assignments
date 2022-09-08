import socket
import time
import threading

from nodeconnection import NodeConnection

"""
We used an example p2p network as a starting point to build the DHT: https://github.com/macsnoeren/python-p2p-network
This is a node class that represents a node in DHT.
Each node has a connection to their successor and an id for next successor.

"""


class Node(threading.Thread):

    def __init__(self, port, id):

        super(Node, self).__init__(daemon=True)

        # When this flag is set, the node will stop and close
        self.terminate_flag = threading.Event()

        # currently for local use only
        self.host = "127.0.0.1"
        self.port = port

        # Events are send back to the given callback
        self.callback = self.node_callback

        self.successor = None
        self.next_successor = None
        self.id = id
        self.shortcuts = []

        # Start the TCP/IP server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

    def node_callback(self, event, main_node, connected_node, data):
        #connect this node to given port
        if event == 'connect':
            self.connect_with_successor(int(data))
            self.get_next_successor()
        #when removing or adding nodes, maintain next_successor consistency
        elif event == 'update_next_successors':
            start = int(data)
            if self.id != start:
                self.get_next_successor()
                self.successor.send(('update_next_successors:%s' % (data)).encode('utf-8'))
        #send successor to previous node
        elif event == 'send_successor':
            connected_node.send(("receive_next_successor:%d" % (self.successor.id)).encode("utf-8"))
        #update next successor
        elif event == 'receive_next_successor':
            self.next_successor = int(data)
        #search for next_successor
        elif event == 'get_next_successor':
            self.get_next_successor()
        

    def init_server(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(10.0)
        self.sock.listen(1)

    def delete_closed_connections(self):
        if self.successor.terminate_flag.is_set():
            self.successor.join()
        if self.next_successor.terminate_flag.is_set():
            self.next_successor.join()

   

    def get_next_successor(self):
        self.successor.send(("send_successor").encode("utf-8"))

    def connect_with_successor(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', port))

            sock.send(str(self.id).encode('utf-8'))
            connected_node_id = sock.recv(4096).decode('utf-8')
            
            #create new NodeConnection
            thread_client = self.create_new_connection(sock, connected_node_id, '127.0.0.1', port)
            thread_client.start()

            self.successor = thread_client

        except Exception as e:
            pass

    def connect_with_shortcut(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', port))

            sock.send(str(self.id).encode('utf-8'))
            connected_node_id = sock.recv(4096).decode('utf-8')

            #create new NodeConnection
            thread_client = self.create_new_connection(sock, connected_node_id, '127.0.0.1', port)
            thread_client.start()

            self.shortcuts.append(thread_client)
            self.shortcuts = sorted(self.shortcuts, key=lambda node: int(node.id))

        except Exception as e:
            pass

    def stop(self):
        self.terminate_flag.set()

    def create_new_connection(self, connection, id, host, port):
        return NodeConnection(self, connection, id, host, port)

    def run(self):
        # Check whether the thread needs to be closed
        while not self.terminate_flag.is_set():
            try:
                connection, client_address = self.sock.accept()

                connected_node_id = connection.recv(4096).decode('utf-8')
                connection.send(str(self.id).encode('utf-8'))

                thread_client = self.create_new_connection(connection, connected_node_id, client_address[0],
                                                           client_address[1])
                thread_client.start()


            except socket.timeout:
                pass
            except Exception as e:
                raise e

            time.sleep(0.01)

        self.successor.stop()

        self.sock.settimeout(None)
        self.sock.close()

    def node_message(self, node, command, data=''):
        # This method is invoked when a node sends a message
        if self.callback is not None:
            self.callback(command, self, node, data)

    def __str__(self):
        return 'Node: {}:{}'.format(self.host, self.port)

    def __repr__(self):
        return '<Node {}:{} id: {}>'.format(self.host, self.port, self.id)
