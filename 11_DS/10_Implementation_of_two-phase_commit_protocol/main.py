#from os import wait
from argon2 import PasswordHasher
from client import Client
from threading import Thread
from twisted.internet import reactor
from time import sleep
import socket
import copy
from time import sleep
import twisted

import sys


def send_list(destination_id):
    ip = "127.0.0.1"
    port = 10000+destination_id
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    string = "list_all;"
    s.sendto(string.encode('utf-8'), (ip, port))


def set_value(destination_id, x):
    ip = "127.0.0.1"
    port = 10000+destination_id
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    string = f"set_value;{x}"
    s.sendto(string.encode('utf-8'), (ip, port))


def rollback(destination_id, n):
    ip = "127.0.0.1"
    port = 10000+destination_id
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    string = f"rollback;{n}"
    s.sendto(string.encode('utf-8'), (ip, port))


def time_failure(destination_id, t):
    ip = "127.0.0.1"
    port = 10000+destination_id
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    string = f"time_failure;{t}"
    s.sendto(string.encode('utf-8'), (ip, port))


def read_file(filename):
    systems = []
    states = []
    with open(filename, mode='rt', encoding='utf-8') as f:
        read_data = f.read().splitlines()
        for line in range(len(read_data)):
            if read_data[line] == '#System':
                line += 1
                while read_data[line] != '#State':
                    if 'Coordinator' in read_data[line]:
                        read_line = read_data[line].split(';')
                        coordinator_id = int(read_line[0][1:])
                    else:
                        systems.append(int(read_data[line][1:]))
                    line += 1
            elif read_data[line] == '#State':
                read_line = read_data[line+1].split(';')
                states = read_line[1].split(',')
                states = [int(n) for n in states]
    return systems, states, coordinator_id


def command_input(command, systems, states, coordinator):
    command = command.split(' ')

    if command[0] == 'List':
        send_list(coordinator)
    elif command[0] == 'Set-value':
        set_value(coordinator, command[1])
    elif command[0] == 'Rollback':
        rollback(coordinator, command[1])
    elif command[0] == 'Time-failure':
        time_failure(int(command[1][1:]), command[2])


if __name__ == "__main__":

    # Read the file and get systems and history both as a list, coordinator as a integer. ex.['P1', 'P2', 'P3', 'P4'], [4, 5, 6, 7, 8, 9]
    systems, states, coordinator = read_file('2PC.txt')
    reactor.listenUDP(10000+coordinator, Client(coordinator, 'localhost',
                      "P"+str(id), copy.deepcopy(states), copy.deepcopy(systems), -1))
    for id in systems:
        reactor.listenUDP(10000+int(id), Client(int(id), 'localhost',
                          "P"+str(id), copy.deepcopy(states), systems, coordinator))
    Thread(target=reactor.run, args=(False,), daemon=True).start()

    command = input()
    while command != 'exit':
        command_input(command, systems, states, coordinator)
        command = input()
