from multiprocessing.connection import wait
import threading
import rpyc
from rpyc.utils.server import ThreadedServer
import datetime
from functools import wraps
from multiprocessing import synchronize
from platform import processor
import datetime
import _thread
from types import coroutine
import time

# global variables
system_start = datetime.datetime.now()
date_time = datetime.datetime.now()
data = None
wait = 10


class ReplicaNode(threading.Thread):
    def __init__(self, type='backup', data=None):
        self.data = data
        self.type = type
        self.wait = 10

    # starts a thread that runs the process
    def start(self):
        _thread.start_new_thread(self.run, ())

    def run(self):
        while True:
            time.sleep(self.wait)
            global data
            global wait
            self.data = data
            self.wait = wait


class MonitorService(rpyc.Service):
    def __init__(self):
        self.main = ReplicaNode(type='main')
        self.nodes = []

    def exposed_create_node(self, num_nodes):
        print(f'Caching time for the update {wait}')
        print(f'The number of threads (other replicas): {num_nodes}')
        for _ in range(num_nodes):
            self.nodes.append(ReplicaNode())
        for n in self.nodes:
            n.start()

    def exposed_run(self, commands):
        comm_arg = commands.split()

        if comm_arg[0].lower() == 'list':
            print(f'Receive commond from Client: {commands}')
            print(f'Data in the main replica: {self.main.data}')
            for n in self.nodes:
                print(f'Data in the other replica: {n.data}')

        elif comm_arg[0].lower() == 'update':
            print(f'Receive commond from Client: {commands}')
            global data
            data = comm_arg[1]
            self.main.data = data
        elif comm_arg[0].lower() == 'cache':
            print(f'Receive commond from Client: {commands}')
            global wait
            wait = int(comm_arg[1])
        elif comm_arg[0].lower() == 'exit':
            print(f'Receive commond from Client: {commands}')
            print('Program exited')

    def on_disconnect(self, conn):
        print("\ndisconneced on {}".format(date_time))

    def on_connect(self, conn):
        print("\nconnected on {}".format(date_time))


if __name__ == '__main__':
    t = ThreadedServer(MonitorService, port=18812)
    t.start()
