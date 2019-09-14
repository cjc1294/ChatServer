import socket
import threading
import os
import atexit
import sys

def exit():
	s.close()

def recieve():	
	try:
		while True:
			incoming = str(s.recv(1024))
			print (incoming[2:-1])
	except RuntimeError:
		pass
	except ConnectionResetError:
		python = sys.executable
		os.execl(python, python, * sys.argv)
	except KeyboardInterrupt:
		mess = 'exit'
		s.send(mess.encode())
		os._exit(0)
def send():
	while True:
		try:
			mess=input()
			if mess == 'quit':
				mess = 'exit'
				s.send(mess.encode())
				os._exit(0)
			s.send(mess.encode())
		except RuntimeError:
			pass
#		except KeyboardInterrupt:
#			mess = 'exit'
#			s.send(mess.encode())
#			os._exit(0)

s = socket.socket()
connected = False
while not connected:
	useIn=input("Server IP: ")
	try:
		if useIn == "":
			print("Connecting to 192.168.1.10")
			s.connect(('192.168.1.10', 12345))
			connected = True
		else:
			print("Connecting to "+useIn)
			s.connect((useIn, 12345))
			connected  = True
	except ConnectionRefusedError:
		print("Error connecting")
mess = ''
print ("Connected")
print ("")
recieveing = threading.Thread(target=recieve)
recieveing.start()
sending = threading.Thread(target=send)
sending.start()
