from random import randint
from operator import itemgetter
import rpyc
from rpyc.utils.server import ThreadedServer
import datetime
import time
import threading
from multiprocessing import Process
import _thread


# global variables
system_start = datetime.datetime.now()
date_time = datetime.datetime.now()
nodes = []
cs_q = []


class Message(object):
    def __init__(self, id=None, timestamp=None):
        self.id = id
        self.timestamp = timestamp


class Process(threading.Thread):

    def __init__(self, id):
        super(Process, self).__init__()
        self.id = id
        self.timestamp = 0
        self.status = 'DO-NOT-WANT'
        self.cst = randint(0, 10)
        self.pt = randint(0, 5)
        self.message = Message()
        self.inTheQ = False
        self.recvAck = []

    def _send_ack(self, message):
        global nodes

        recever = next((x for x in nodes if x.id == message.id), None)
        recever.recvAck.append({'sender': self.id, 'msg': 'OK'})
        recever.timestamp = max(recever.timestamp, self.timestamp)+1
        print(f'node {self.id} send OK to {recever.id}')

    def _release_cs(self, next_node):
        global nodes
        self.status = 'DO-NOT-WANT'
        if next_node != None:
            recever = next((x for x in nodes if x.id == next_node.id), None)
            recever.recvAck.append({'sender': self.id, 'msg': 'OK'})
            recever.timestamp = max(recever.timestamp, self.timestamp)+1
            print(f'node {self.id} release CS and give it to {recever.id}')
            self.timestamp += 1
        else:
            print('No HOLDER')
            self.timestamp += 1

    def handel_receive_message(self, message):
        if self.status == 'DO-NOT-WANT':
            self.timestamp = max(self.timestamp, message.timestamp)+1
            self._send_ack(message)
        elif self.status == 'WANTED':
            if self.timestamp == message.timestamp:
                if self.id > message.id:
                    self._send_ack(message)
            elif self.timestamp > message.timestamp:
                self._send_ack(message)
            else:
                pass
        elif self.status == 'HELD':
            pass

    def _check_status(self):
        global nodes
        global cs
        global cs_q

        if self.status == 'DO-NOT-WANT':
            time.sleep(self.pt)
            self.status = 'WANTED'
            self.timestamp += 1
        elif self.status == 'WANTED':
            if self.inTheQ is False:
                self.message = Message(self.id, self.timestamp)
                self.inTheQ = True
                print(
                    f'node {self.id} send the timestamp: {self.message.timestamp}')
                send_message(self.message)
            if len(self.recvAck) == (len(nodes)-1):
                remove = cs_q.pop(0)
                print(f'node {self.id} remove {remove.id}')
                for q in cs_q:
                    print(q.id,q.timestamp)
                self.inTheQ = False
                self.recvAck = []
                self.status = 'HELD'
                self.timestamp += 1
        elif self.status == 'HELD':
            time.sleep(self.cst)
            if len(cs_q) == 0:
                self._release_cs(None)
            else:
                self._release_cs(cs_q[0])

    # starts a thread that runs the process
    def start(self):
        _thread.start_new_thread(self.run, ())

    def run(self):
        global q

        while True:
            t = threading.Thread(target=self._check_status())
            t.daemon = True
            t.start()
            t.join()


# Simulate sokect function
def send_message(message):
    global cs_q
    global nodes

    cs_q.append(message)
    cs_q.sort(key=lambda x: (x.timestamp,x.id))
    for n in nodes:
        if n.id==message.id:
            pass
        else:
            n.handel_receive_message(message)


class MonitorService(rpyc.Service):
    def exposed_run(self, num_nodes):
        global nodes

        for i in range(int(num_nodes)):
            nodes.append(Process(i+1))

        # Activate process
        for n in nodes:
            n.name = str(n.id)
            n.daemon = True
            n.start()

    def exposed_update_cst(self, t):
        global nodes
        for n in nodes:
            n.cst = randint(10, t)

    def exposed_update_pt(self, t):
        global nodes
        for n in nodes:
            n.pt = randint(5, t)

    def exposed_show_list(self):
        global nodes
        for n in nodes:
            print(f'{n.id}, {n.status}')


def on_disconnect(self, conn):
    print("\ndisconneced on {}".format(date_time))


def on_connect(self, conn):
    print("\nconnected on {}".format(date_time))


if __name__ == '__main__':
    t = ThreadedServer(MonitorService, port=18812)
    t.start()
