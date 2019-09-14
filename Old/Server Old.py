import socket
import os
import threading
import sys

clients=[]

def recieve(c, addr):
	try:
		while True:
			incomingMess = str(c.recv(1024))
			if incomingMess[-7:] == 'b\'exit\'':
				print('Connection closed')
				break
				print('Exiting Failed')
			print (str(addr)+": "+incomingMess[2:-1])
			outgoing=str(addr)+": "+str(incomingMess[2:-1])
			for i in range(len(clients)):
				client = clients[i]
				client.send(outgoing.encode())
	except ConnectionResetError:
		print ("Client has disconnected")
		python = sys.executable
		os.execl(python, python, * sys.argv)
		pass
	except ConnectionAbortedError:
		print ("Client has disconnected")
		python = sys.executable
		os.execl(python, python, * sys.argv)
		pass


def send(c):
	while True:
		mess="Server: "+input()
		for i in range(len(clients)):
			client = clients[i]
			client.send(mess.encode())

def main():
	try:
		c, addr = s.accept()
		clients.append(c)
		connection=str(addr)
		print ("Connection from: "+connection)
		connectionMess="Connection from "+connection
		for i in range(len(clients)):
			client = clients[i]
			client.send(connectionMess.encode())
		recieveing = threading.Thread(target=recieve, args=[c, addr])
		sending = threading.Thread(target=send, args=[c])
		recieveing.start()
		sending.start()
	except RuntimeError:
		pass

s = socket.socket()
print ("Socket created")
s.bind(('', 12345))
print ("Socket bound")
s.listen()
print ("Socket listening")
print ('')
print ('')
mess=''

while True:
	main()