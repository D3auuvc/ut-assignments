import rpyc
import sys
 
if len(sys.argv) < 2:
   exit("Usage {} SERVER".format(sys.argv[0]))
 
server = sys.argv[1]
conn = rpyc.connect(server, 18812)

input_text = input("Input the file name: ")
commands = []
while True:
   command = input("Input the command: ")
   commands.append(command)
   if command == "exit":
      break
   conn.root.exposed_clock_sync(input_text, commands)