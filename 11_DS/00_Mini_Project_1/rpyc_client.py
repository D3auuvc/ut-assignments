import rpyc
import sys

if len(sys.argv) < 2:
   exit("Usage {} SERVER".format(sys.argv[0]))

# server = sys.argv[1]
_SERVER = 'localhost'
conn = rpyc.connect(_SERVER, 18812)

num_nodes = sys.argv[1]
conn.root.run(num_nodes)

while True:
   command = input("Input the command: ")
   cmd_lst = command.split(' ')

   if cmd_lst[0].lower() == 'time-cs':
      if int(cmd_lst[1]) < 10:
         print('The time should greater than 10')
      else:
         conn.root.update_cst(int(cmd_lst[1]))
   elif cmd_lst[0].lower() == 'list':
      conn.root.show_list()
   elif cmd_lst[0].lower() == 'time-p':
      if int(cmd_lst[1]) < 5:
         print('The time should greater than 5')
      else:
         conn.root.update_pt(int(cmd_lst[1]))

   if command == "exit":
      break
