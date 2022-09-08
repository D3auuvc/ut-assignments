#!/usr/bin/env python
from __future__ import print_function
from pysyncobj import SyncObj, SyncObjConf, replicated

import sys
sys.path.append("../")


class KVStorage(SyncObj):
    def __init__(self, selfAddress, partnerAddrs):
        cfg = SyncObjConf(dynamicMembershipChange=True)
        super(KVStorage, self).__init__(selfAddress, partnerAddrs, cfg)
        self.__data = {}
        self.__index = 0

    @replicated
    def set(self, key, value):
        self.__index += 1
        self.__data[key] = value
        return ((self.__data[key], self.__index))

    @replicated
    def pop(self, key):
        self.__index += 1
        try:
            self.__data.pop(key)
        except KeyError:
            pass

    def get(self, key):
        return (self.__data.get(key, None), self.__index)


_g_kvstorage = None


def main():
    if len(sys.argv) < 2:
        print('Usage: %s selfHost:port partner1Host:port partner2Host:port ...')
        sys.exit(-1)

    selfAddr = sys.argv[1]
    if selfAddr == 'readonly':
        selfAddr = None
    partners = sys.argv[2:]

    global _g_kvstorage
    _g_kvstorage = KVStorage(selfAddr, partners)

    def get_input(v):
        if sys.version_info >= (3, 0):
            return input(v)
        else:
            return raw_input(v)

    while True:
        cmd = get_input(">> ").split()
        if not cmd:
            continue
        elif cmd[0] == 'set':
            _g_kvstorage.set(cmd[1], cmd[2])
        elif cmd[0] == 'get':
            print(_g_kvstorage.get(cmd[1]))
        elif cmd[0] == 'pop':
            print(_g_kvstorage.pop(cmd[1]))
        else:
            print('Wrong command')


if __name__ == '__main__':
    main()
