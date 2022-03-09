import rpyc
import sys
 
if len(sys.argv) < 2:
   exit("Usage {} SERVER".format(sys.argv[0]))
 
server = sys.argv[1]

try:
    conn = rpyc.connect(server,18812)
    conn.root.test_random()
    print('Success: it works!')
except Exception as e:
    raise Exception("Fail")
    