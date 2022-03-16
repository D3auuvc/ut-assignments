import rpyc
from rpyc.utils.server import ThreadedServer
import datetime
import time
from functools import wraps
from platform import processor
from types import coroutine
import threading
#from Queue import Queue
#import Queue
from multiprocessing import Queue
from multiprocessing import synchronize

initially_granted_proc = "A"
procs = {"A", "B", "C"}
resource_usage_counts = {"A": 0, "B": 0, "C": 0}
message_queues = {"A": Queue(), "B": Queue(), "C": Queue()}

# global variables
processes = []
date_time = datetime.datetime.now()
system_start = datetime.datetime.now()


class Message(object):
    def __init__(self, msg_type, timestamp, sender, receiver):
        self.msg_type = msg_type
        self.timestamp = timestamp
        self.sender = sender
        self.receiver = receiver

    def __repr__(self):
        return "Message {} at {} from {} to {}".format(
            self.msg_type, self.timestamp,
            self.sender, self.receiver)


class Process(threading.Thread):

    def __init__(self, name, initially_granted, other_processes):
        super(Process, self).__init__()
        self.name = name
        self.has_resource = initially_granted == name
        self.other_processes = other_processes
        self.lamport_clock = 0  # tick after each "event"
        self.request_queue = []
        self.requested = False
        self.request_queue.append(Message("request",
                                          -1, initially_granted, initially_granted))

    def remove_request(self, msg_type, sender):
        index_of_req = -1
        for i in range(len(self.request_queue)):
            if self.request_queue[i].msg_type == msg_type and \
               self.request_queue[i].sender == sender:
                index_of_req = i
                break
        if i == -1:
            print("Unable to remove")
        else:
            del self.request_queue[i]

    def use_resource(self):
        print("Process {} is using resource".format(self.name))
        resource_usage_counts[self.name] += 1
        time.sleep(2)

    def process_message(self, msg):
        # Based on msg_type handle appropriately
        if msg.msg_type == "request":
            # Put in our request queue and send an ack
            # to the sender
            self.request_queue.append(msg)
            for proc in self.other_processes:
                if proc == msg.sender:
                    message_queues[proc].put(Message(
                    	"ack", self.lamport_clock,
                    	self.name, msg.sender))
        elif msg.msg_type == "release":
            # Got a release, remove it from our queue
            self.remove_request("request", msg.sender)
        elif msg.msg_type == "ack":
            pass
        else:
            print("Unknown message type")

    def run(self):
        while True:
            if self.has_resource:
                self.use_resource()
                self.remove_request("request", self.name)
                # Tell everyone that we are done
                for proc in self.other_processes:
                    message_queues[proc].put(Message(
                    	"release", self.lamport_clock,
                    	self.name, proc))
                    self.lamport_clock += 1
                self.has_resource, self.requested = False, False
                continue
            # Want to get the resource
            if not self.requested:
                # Request it
                print("Process {} requesting resource".format(
                    self.name))
                self.request_queue.append(Message(
                    "request", self.lamport_clock,
                   	self.name, self.name))
                # Broadcast this request
                for proc in self.other_processes:
                    message_queues[proc].put(Message(
                    	"request", self.lamport_clock,
                    	self.name, proc))
                    self.lamport_clock += 1
                self.requested = True
            else:
                # Just wait until it is available by processing messages
                print("Process {} waiting for message".format(self.name))
                msg = message_queues[self.name].get(block=True)
                # Got a message, check if the timestamp
                # is greater than our clock, if so advance it
                if msg.timestamp >= self.lamport_clock:
                    self.lamport_clock = msg.timestamp + 1
                print("Got message {}".format(msg))
                self.process_message(msg)
                self.lamport_clock += 1
                # Check after processing if the resource is
                # available for me now, if so, grab it.
                # We need earliest request to be ours and check that we
                # have received an older message from everyone else
                if self.check_available():
                    print("Resource available for {}".format(self.name))
                    self.has_resource = True
            print("Process {}: {}".format(self.name, self.request_queue))
            print("Process {} Clock: {}".format(self.name, self.lamport_clock))
            time.sleep(1)

    def check_available(self):
        got_older = {k: False for k in self.other_processes}
        # Get timestamp of our req
        our_req = None
        for req in self.request_queue:
            if req.sender == self.name:
                our_req = req
        if our_req is None:
            return False
        # We found our req make sure it is younger than
        # all the others and we have an older one from
        # the other guys
        for req in self.request_queue:
            if req.sender in got_older and req.timestamp > our_req.timestamp:
                got_older[req.sender] = True
        if all(got_older.values()):
            return True
        return False


class MonitorService(rpyc.Service):
    def exposed_run(self):
        initially_granted_proc = "A"
        procs = {"A", "B", "C"}
        resource_usage_counts = {"A": 0, "B": 0, "C": 0}
        message_queues = {"A": Queue(), "B": Queue(), "C": Queue()}
        t1 = Process("A", initially_granted_proc, list(procs - set("A")))
        t2 = Process("B", initially_granted_proc, list(procs - set("B")))
        t3 = Process("C", initially_granted_proc, list(procs - set("C")))

        t1.setDaemon(True)
        t2.setDaemon(True)
        t3.setDaemon(True)

        t1.start()
        t2.start()
        t3.start()
        while True:
            t1.join(10)
            t2.join(10)
            t3.join(10)


def on_disconnect(self, conn):
    print("\ndisconneced on {}".format(date_time))


def on_connect(self, conn):
    print("\nconnected on {}".format(date_time))


if __name__ == '__main__':
    t = ThreadedServer(MonitorService, port=18812)
    t.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("Ctrl-c pressed")
        print("Resource usage:")
        print(resource_usage_counts)
        quit()
