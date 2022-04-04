from random import randint
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


class Message(object):
    def __init__(self, id=None, timestamp=None):
        self.id = id
        self.timestamp = timestamp


class Process(threading.Thread):

    def __init__(self, id, threadLock, nodes):
        super(Process, self).__init__()
        self.id = id
        self.timestamp = 0
        self.status = 'DO-NOT-WANT'
        self.cst = randint(0, 10)
        self.pt = randint(0, 5)
        self.message = Message()
        self.inTheQ = False
        self.recvAck = []
        self.waitForResponse = []
        self.mutex = threadLock
        self.nodes = nodes

    def _send_ack(self, message):
        recever = next((x for x in self.nodes if x.id == message.id), None)
        recever.recvAck.append({'sender': self.id, 'msg': 'OK'})
        recever.timestamp = max(recever.timestamp, self.timestamp)+1
        print(f'node {self.id} send OK to {recever.id}')

    def _release_cs(self):
        self.status = 'DO-NOT-WANT'
        self.mutex.release()
        if len(self.waitForResponse) != 0:
            for wn in self.waitForResponse:
                self.timestamp += 1
                recever = next((x for x in self.nodes if x.id == wn.id), None)
                recever.recvAck.append({'sender': self.id, 'msg': 'OK'})
                recever.timestamp = max(recever.timestamp, self.timestamp)+1                
            self.waitForResponse = []
        else:
            self.timestamp += 1

    def handel_receive_message(self, message):
        if self.status == 'DO-NOT-WANT':
            self.timestamp = max(self.timestamp, message.timestamp)+1
            self._send_ack(message)
        elif self.status == 'WANTED':
            if self.timestamp == message.timestamp:
                if self.id > message.id:
                    self._send_ack(message)
                else:
                    self.waitForResponse.append(message)
            elif self.timestamp > message.timestamp:
                self._send_ack(message)
            else:
                self.waitForResponse.append(message)
        elif self.status == 'HELD':
            self.waitForResponse.append(message)

    # Simulate sokect function
    def _send_message(self, message):
        for n in self.nodes:
            if n.id == message.id:
                pass
            else:
                n.handel_receive_message(message)

    def _check_status(self):
        if self.status == 'DO-NOT-WANT':
            time.sleep(self.pt)
            self.status = 'WANTED'
            self.timestamp += 1
        elif self.status == 'WANTED':
            if self.inTheQ is False:                
                self.inTheQ = True
                print(f'node {self.id} send the timestamp: {self.message.timestamp}')
                self.timestamp += 1
                self.message = Message(self.id, self.timestamp)
                self._send_message(self.message)
            if len(self.recvAck) == (len(self.nodes)-1):
                self.inTheQ = False
                self.recvAck = []
                self.mutex.acquire()
                self.status = 'HELD'
                self.timestamp += 1
        elif self.status == 'HELD':
            for n in self.nodes:
                print(f'{n.id}, {n.status}, {n.recvAck}')
            time.sleep(self.cst)
            self._release_cs()

    # starts a thread that runs the process
    def start(self):
        _thread.start_new_thread(self.run, ())

    def run(self):
        while True:
            t = threading.Thread(target=self._check_status())
            t.daemon = True
            t.start()
            t.join()


class MonitorService(rpyc.Service):
    def __init__(self):
        self.nodes = []
        self.threadLock = threading.Lock()

    def exposed_run(self, num_nodes):
        for i in range(int(num_nodes)):
            self.nodes.append(Process(i+1, self.threadLock, self.nodes))

        # Activate process
        for n in self.nodes:
            n.name = str(n.id)
            n.daemon = True
            n.start()

    def exposed_update_cst(self, t):
        for n in self.nodes:
            n.cst = randint(10, t)

    def exposed_update_pt(self, t):
        for n in self.nodes:
            n.pt = randint(5, t)

    def exposed_show_list(self):
        for n in self.nodes:
            print(f'{n.id}, {n.status}')


def on_disconnect(self, conn):
    print("\ndisconneced on {}".format(date_time))


def on_connect(self, conn):
    print("\nconnected on {}".format(date_time))


if __name__ == '__main__':
    t = ThreadedServer(MonitorService, port=18812)
    t.start()
