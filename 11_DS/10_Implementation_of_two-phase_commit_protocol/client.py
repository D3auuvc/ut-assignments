import string
from pyparsing import null_debug_action
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from time import sleep


class Client(DatagramProtocol):
    def __init__(self, id, host, name, history, participants, coordinator_id):
        if host == "localhost":
            self.host = "127.0.0.1"

        self.name = name.split('_')[0]
        self.id = id
        self.alive = True
        self.value = history[-1]
        self.history = history
        self.ready = []
        self.receive_reply = []
        self.participants = participants
        self.waiting_state = False
        self.waiting_counter = 0
        self.transaction_value = None
        self.listen_counter = 0
        self.respond_counter = 0
        self.listen_time = 0
        self.respond_time = 0
        self.respond_state = True
        self.listen_state = True
        self.coordinator = coordinator_id
        self.decision = None

    def datagramReceived(self, datagram: bytes, addr, x=None):
        datagram = datagram.decode('utf-8')
        self.process_datagram(datagram)

    def startProtocol(self):
        reactor.callInThread(self.time_tick)

    def time_tick(self):
        while self.alive:
            sleep(0.01)
            if self.waiting_state:
                self.waiting_counter += 1
                if self.waiting_counter > 100:
                    self.handle_bad()
            if not self.listen_state:
                self.listen_counter += 1
                if self.listen_counter > self.listen_time * 100:
                    self.listen_state = True
            if not self.respond_state:
                self.respond_counter += 1
                if self.respond_counter > self.respond_time * 100:
                    self.respond_state = True

    def process_datagram(self, string):
        splits = string.split(";")
        function = splits[0]

        if function == "bad" and self.listen_state:
            self.handle_bad()

        elif function == "abort" and self.listen_state:
            self.abort_transaction()

        # Show the coordinator
        elif function == "list_all" and self.listen_state:
            print("P" + str(self.id), "coordinator", self.history)
            print(self.participants)
            self.broadcast_list()

        # Show the list of participants
        elif function == "list" and self.listen_state:
            print("P" + str(self.id), self.value,
                  self.respond_state, self.history)

        # Set-value X -- This command sends a new value “X” to the system (to be committed)
        elif function == "set_value" and self.listen_state:
            self.vote_request(function, int(splits[1]))

        # Participants send the vote to coordinator
        elif function == "vote" and self.listen_state:
            self.send_vote(splits[2], int(splits[1]))

        # Coordinator collects votes
        elif function == "send_reply" and self.listen_state:
            self.receive_reply.append(splits[1])

            # If collects all votes
            if len(self.receive_reply) == len(self.participants):
                if self.receive_reply.count('VOTE-ABORT') == 0:
                    self.decision = 'COMMIT'
                    self.global_commit(function=splits[2])
                else:
                    self.decision = 'ABORT'
                    self.global_abort(function=splits[2])

        # Participant commit the value
        elif function == "commit" and self.listen_state:
            self.apply_change(splits[1])

        # Send ACK to coordinator after commit
        elif function == "send_ack" and self.listen_state:
            self.ready.append(splits[1])

            # If collects all acks
            if len(self.ready) == len(self.participants):
                commit_function = splits[2]
                if self.decision == 'COMMIT':
                    if commit_function == 'set_value':
                        self.history.append(self.transaction_value)
                        self.value = self.transaction_value
                    elif commit_function == 'rollback':
                        del self.history[self.transaction_value:]
                        self.value = self.history[-1]

                    # init
                    self.transaction_value = None
                    self.waiting_state = False
                    self.ready = []
                    self.receive_reply = []
                elif self.decision == 'ABORT':
                    # init
                    self.abort_transaction()
                    self.waiting_state = False
                    self.ready = []
                    self.receive_reply = []

        # Rollback N --This command rolls back to previous values based on a number N of positions.
        # For simplicity, all values after the rolled back value are forgotten by the system.
        elif function == "rollback" and self.listen_state:
            if len(self.history) > int(splits[1]):
                forgotten_value = len(self.history) - int(splits[1])
                self.vote_request(function, forgotten_value)
            else:
                print("The system cannot reverse to that long state")

        # Time-failure PX time -- It makes a specific process “PX” unavailable in the system for a period of “time” in seconds. 
        # This means that the process cannot be reached nor respond to any external request. After the time is over, 
        # the process becomes again available and continues its normal operations.
        elif function == "time_failure" and self.listen_state:
            self.respond_state = False
            self.respond_time = int(splits[1])

    # end of 'process_datagram'

    def handle_bad(self):
        self.waiting_state = False
        self.broadcast_abort()

    def abort_transaction(self):
        self.transaction_value = None

    def broadcast_abort(self):
        for id in self.participants:
            self.send_abort(id)

    def broadcast_list(self):
        for id in self.participants:
            self.send_list(id)

    def send_abort(self, destination_id):
        string = "abort;"
        addr = self.host, 10000+destination_id
        self.transport.write(string.encode('utf-8'), addr)

    def send_list(self, destination_id):
        string = "list;"
        addr = self.host, 10000+destination_id
        self.transport.write(string.encode('utf-8'), addr)

    # commit value
    def commit(self, destination_id):
        string = "commit;"
        addr = self.host, 10000+destination_id
        self.transport.write(string.encode('utf-8'), addr)

    # Coordinator send 'VOTE-REQUEST' to participants and collects votes from participants,
    # and send 'GLOBAL-COMMIT' if there is no 'VOTE-ABORT', otherwise,  send 'GLOBAL-ABORT'.
    def vote_request(self, function: string, x: int):
        msg = "VOTE-REQUEST"
        self.waiting_state = True
        self.transaction_value = x

        # Send 'VOTE-REQUEST' to participants
        for id in self.participants:
            self.send_msg_to_participant(id, function, msg, x)

    # Send 'GLOBAL-COMMIT' to all participants
    def global_commit(self, function: string):
        msg = "GLOBAL-COMMIT"
        for id in self.participants:
            self.send_msg_to_participant(id, function, msg)

    def global_abort(self, function: string):
        msg = "GLOBAL-ABORT"
        self.waiting_state = False
        for id in self.participants:
            self.send_msg_to_participant(id, function, msg)

    # Receive message from coordinator
    def send_msg_to_participant(self, destination_id, function: string, msg: string, x: int = None):
        if msg == 'VOTE-REQUEST':
            string = f"vote;{x};{function}"
        elif msg == 'GLOBAL-COMMIT':
            string = f"commit;{function}"
        elif msg == 'GLOBAL-ABORT':
            string = f"abort;"

        addr = self.host, 10000+destination_id
        self.transport.write(string.encode('utf-8'), addr)

    # Participants send vote to coordinator
    def send_vote(self, function: string, x: int):
        self.waiting_state = True
        if self.respond_state:
            string = f"send_reply;VOTE-COMMIT;{function}"
            self.transaction_value = x
        else:
            string = f"send_reply;VOTE-ABORT;{function}"
            self.abort_transaction()

        addr = self.host, 10000+self.coordinator
        self.transport.write(string.encode('utf-8'), addr)

    # Commit change
    def apply_change(self, function: string):
        if function == 'set_value':
            self.history.append(self.transaction_value)
            self.value = self.transaction_value
        elif function == 'rollback':
            del self.history[self.transaction_value:]
            self.value = self.history[-1]

        self.waiting_state = False
        self.transaction_value = None

        string = f"send_ack;ACK;{function}"
        addr = self.host, 10000+self.coordinator
        self.transport.write(string.encode('utf-8'), addr)
