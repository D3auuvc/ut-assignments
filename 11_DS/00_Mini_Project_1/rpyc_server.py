import _thread
import datetime
import threading
import time
from multiprocessing import Process
from random import randint

import rpyc
from rpyc.utils.server import ThreadedServer

# global variables
system_start = datetime.datetime.now()
date_time = datetime.datetime.now()


class Message(object):
    """
    To simulate REQUEST content in algorithm, encapsulates id and timestamp
    """

    def __init__(self, id=None, timestamp=None):
        """
        Construct a new 'Message' object.

        :param id       : The id of sender
        :param timestamp: The lamport timestamp
        :return         : Returns nothing
        """
        self.id = id
        self.timestamp = timestamp


class Process(threading.Thread):
    """
    To simulate client (node) in Distributed Systems
    """

    def __init__(self, id, threadLock, nodes):
        """
        Construct a new 'Process' thread.
        
        :param id           : The id of client (node)
        :param threadLock   : The thread Lock object to handel mutual exclusion
        :param nodes        : the list of client(node) in Distributed Systems
        :return             : Returns nothing
        """
        super(Process, self).__init__()
        self.id = id                # client id
        self.timestamp = 0          # lamport timestamp
        self.status = 'DO-NOT-WANT' # client status
        self.cst = randint(0, 10)   # holding time of critical section
        self.pt = randint(0, 5)     # waiting time for switching status to 'WANTED'
        self.message = Message()    # REQUEST message object
        self.inTheQ = False         # flag for 'WANTED' status
        self.recvAck = []           # list of receive acknowledge
        self.waitForResponse = []   # list of REPLY holding
        self.mutex = threadLock     # thread Lock object to handel mutual exclusion
        self.nodes = nodes          # the list of client(node) in Distributed Systems

    def _send_ack(self, message):
        """
        To simulate send a REPLY(acknowledge) message to REQUEST sender.

        :param message  : The REQUEST message object from sender
        :return         : Returns nothing
        """
        recever = next((x for x in self.nodes if x.id == message.id), None)
        recever.recvAck.append({'sender': self.id, 'msg': 'OK'})
        recever.timestamp = max(recever.timestamp, self.timestamp)+1
        # print(f'node {self.id} send OK to {recever.id}')

    def _release_cs(self):
        """
        To simulate release critical section (CS) and 
        send a REPLY(acknowledge) message to REQUEST sender in REPLY holding list.

        :return: Returns nothing
        """
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
        """
        To simulate mechanism when receive REQUEST message.

        :param message  : The REQUEST message object from sender
        :return         : Returns nothing
        """
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
        """
        To simulate mechanism when switching status to 'WANTED'.

        :param message  : The REQUEST message object from sender
        :return         : Returns nothing
        """
        for n in self.nodes:
            if n.id == message.id:
                pass
            else:
                n.handel_receive_message(message)

    def _check_status(self):
        """
        To simulate mechanism when in each status.

        :return: Returns nothing
        """
        if self.status == 'DO-NOT-WANT':
            time.sleep(self.pt)
            self.status = 'WANTED'
            self.timestamp += 1
        elif self.status == 'WANTED':
            if self.inTheQ is False:
                self.inTheQ = True
                # print(f'node {self.id} send the timestamp: {self.message.timestamp}')
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
            # for n in self.nodes:
            #     print(f'{n.id}, {n.status}, {n.recvAck}')
            time.sleep(self.cst)
            self._release_cs()

    def start(self):
        """
        Starts a thread that runs the process.

        :return: Returns nothing
        """
        _thread.start_new_thread(self.run, ())

    def run(self):
        """
        Runs the process.

        :return: Returns nothing
        """
        while True:
            t = threading.Thread(target=self._check_status())
            t.daemon = True
            t.start()
            t.join()


class MonitorService(rpyc.Service):
    """
    To simulate server in Distributed Systems
    """

    def __init__(self):
        """
        Construct a new server.

        :return         : Returns nothing
        """
        self.nodes = [
        ]                     # list of client(node) in Distributed Systems
        # thread Lock object to handel mutual exclusion
        self.threadLock = threading.Lock()

    def exposed_run(self, num_nodes):
        """
        Starts a Distributed Systems.
        
        :param num_nodes    : Number(N>0) of clients(nodes) in Distributed Systems
        :return             : Returns nothing
        """
        for i in range(int(num_nodes)):
            self.nodes.append(Process(i+1, self.threadLock, self.nodes))

        # Activate process
        for n in self.nodes:
            n.name = str(n.id)
            n.daemon = True
            n.start()

    def exposed_update_cst(self, t):
        """
        To modify upper bound of CS holding time
        
        :param t    : time for setting upper bound of CS holding time
        :return     : Returns nothing
        """
        print(f'Receive command "time-cs {t}"')
        for n in self.nodes:
            n.cst = randint(10, t)
            print(f'change node {n.id} time-out for possessing CS to: {n.cst}')

    def exposed_update_pt(self, t):
        """
        To modify upper bound of time for switching status to 'WANTED'.
                
        :param t    : time for setting time upper bound for switching status to 'WANTED'
        :return     : Returns nothing
        """
        
        print(f'Receive command "time-p {t}"')
        for n in self.nodes:
            n.pt = randint(5, t)
            print(f'change node {n.id} time-out to: {n.pt}')

    def exposed_show_list(self):
        """
        To show the list of clients(nodes) in Distributed Systems.
                
        :return     : Returns nothing
        """
        print(f'Receive command "list"')
        for n in self.nodes:
            print(f'{n.id}, {n.status}')


def on_disconnect(self, conn):
    print("\ndisconneced on {}".format(date_time))


def on_connect(self, conn):
    print("\nconnected on {}".format(date_time))


if __name__ == '__main__':
    t = ThreadedServer(MonitorService, port=18812)
    t.start()
