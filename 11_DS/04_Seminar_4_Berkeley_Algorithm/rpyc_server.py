import rpyc
from rpyc.utils.server import ThreadedServer
import datetime
from functools import wraps
import time
date_time=datetime.datetime.now()
import random
from multiprocessing import synchronize
from platform import processor
import sys
import datetime
import _thread
import time
from types import coroutine

# global variables
processes = []
system_start = datetime.datetime.now()

class Process:
    def __init__(self, id, name, time, label):
        self.id = id
        self.name = name
        self.time = time
        self.label = label
        self.elections = 0
        self.time_start = time
        self.set_time = time

    # starts a thread that runs the process
    def start(self):
        _thread.start_new_thread(self.run, ())

    def run(self):
        # with 5 second interval, update clock
        while True:
            time.sleep(5)
            # self.update_clock()


def tick(running, processes):
    # program ticks evey second
    # to update the coordinator time
    # other processes update clock by Berkeley algorithm
    while running:
        time.sleep(1)
        for p in processes:
            # if p.coordinator and p.coordinator.id == p.id:
            if p.label == "C":
                system_time = datetime.datetime.now()
                # how much time passed since program started
                time_diff = system_time - system_start

                ct = p.set_time
                today = datetime.date.today()
                t = datetime.datetime(today.year, today.month,
                                      today.day, ct.hour, ct.minute, ct.second)
                nt = t + time_diff
                # update time based on difference
                p.time = datetime.time(nt.hour, nt.minute, nt.second)


def list(processes):
    # utility method to list proceeses
    for p in processes:
        if p.label == "C":
            print("%d, %s_%d, %s" %
                  (p.id, p.name, p.elections, "(Coordinator)"), end="\n")
        else:
            print("%d, %s_%d" % (p.id, p.name, p.elections), end="\n")


def clock(processes):
    # utility method to list clocks
    for p in processes:
        # p.update_clock()
        print("%s_%d," %
              (p.name, p.elections), p.time.strftime("%H:%M:%S"))

def kill (kill_p, processes):
    i = 0
    for p in processes:
        if int(p.id) == kill_p and p.label != "C":
            processes.pop(i)
            break
        i += 1
    return processes

def synchronize_time(processes):
    cordinator = 0
    for p in processes:
        if p.label == "C":
            break
        cordinator += 1
    for p in processes:
        if p.label != "C":
            p.time = processes[cordinator].time
    return processes

def parse_lines(lines):
    # utility method to arse input
    result = []
    for l in lines:
        p = l.split(",")
        id = int(p[0].strip())
        name = p[1].strip().split("_")[0]
        time = p[2].strip(" apm").split(":")
        h = int(time[0])
        m = int(time[1])
        s = 0
        t = datetime.time(h, m, s)
        label = p[3].strip()
        result.append([id, name, t, label])
    return result

class MonitorService(rpyc.Service):
    def exposed_clock_sync(self, input_text, commands):
        print("Receive file name from client:", input_text)
        if len(input_text) > 1:
            try:
                fname = input_text
                with open(fname) as f:
                    lines = [line.rstrip('\n') for line in f.readlines()]
                    lines = [line for line in lines if len(
                        line) > 0 and line[0].isdigit()]
                    parsed = parse_lines(lines)
                    ids = []
                    for p in parsed:
                        if p[0] not in ids:
                            # print(p[3])
                            processes.append(Process(p[0], p[1], p[2], p[3]))
                            ids.append(p[0])
                        else:
                            print("[WARNING] Duplicate procees id %d discarded" % p[0])
            except:
                print("[ERROR] Failed to parse the input file.")
                print("Loading default test values.")
        else:
            print("[WARNING] No input file provided.")
            print("Loading default test values.")

        print("Commands: exit, list, clock, kill")

        # start threads of all processes
        for p in processes:
            p.start()

        # start the main loop
        running = True

        # start a separate thread for system tick
        _thread.start_new_thread(tick, (running, processes))
        
        for command_command in commands:
            inp = command_command.lower()
            cmd = inp.split(" ")

            command = cmd[0]
            print("Receive command from client:", command_command)

            _thread.start_new_thread(tick, (running, processes))
            if len(cmd) > 3:
                print("Too many arguments")

            # handle exit
            elif command == "exit":
                running = False
                print("Program exited")


            # handle list
            elif command == "list":
                try:
                    list(processes)
                except:
                    print("Error")

            # handle clock
            elif command == "clock":
                try:
                    clock(processes)
                    synchronize_time(processes)
                except:
                    print("Error")

            elif command == "kill":
                try:
                    kill(int(cmd[1]), processes)
                except:
                    print("Error")

            # handle unsupported command
            else:
                print("Unsupported command:", inp)

    def on_disconnect(self, conn):
        print("\ndisconneced on {}".format(date_time))
        
    def on_connect(self, conn):
        print("\nconnected on {}".format(date_time))

 
if __name__=='__main__':
 t=ThreadedServer(MonitorService, port=18812)

 t.start()