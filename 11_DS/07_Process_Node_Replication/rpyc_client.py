import rpyc
import sys

if len(sys.argv) < 2:
   exit("Usage {} SERVER".format(sys.argv[0]))

server = sys.argv[1]
conn = rpyc.connect(server, 18812)

cmd_args = []
not_set = True
while not_set:
   threads = input('The number of threads (other replicas) created: ')
   cmd_args = threads.split(' ')
   if cmd_args[0].lower() == 'program':
      conn.root.create_node(int(cmd_args[1]))
      not_set = False
   else:
      print('Wrong, Try again')


while True:

   command = input("Input the command: ")
   if command == "exit":
      break
   conn.root.run(command)
