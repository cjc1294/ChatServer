import socket
import threading
import time
import os

global s
global clients
clients = []

class NewClient:
	global clients
	clientObj=''
	clientAddr=''
	username = ''
	stopped = False
	def recieve(self, c, addr):
		self.clientObj=c
		self.clientAddr=addr
		clients.append(self)
		while True:
			if self.stopped:
				break
			try:
				rawMess = self.clientObj.recv(1024)
				incomingMess = rawMess.decode()
				if not incomingMess.startswith('GET') and not incomingMess=='':
					sendAll(incomingMess)
				else:
					print(incomingMess)
			except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
				break

#Send to all connected clients
def sendAll(outgoing):
	global clients
	print(outgoing)
	if len(clients)>=1:
		newClients = list(clients)
		i = 0
		for client in clients:
			try:
				client.clientObj.send(outgoing.encode())
			except(ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
				client.stopped = True
				try:
					del newClients[i]
				except IndexError:
					pass
				pass
			i += 1
		clients = newClients

#Create socket
s = socket.socket()
s.bind(('', 1246))
s.listen()
print('Server Online')
print('')

#Main Loop
while True:
	c, addr = s.accept()
	try:
		incomingClient = NewClient()
		newThread = threading.Thread(target=incomingClient.recieve, args=(c, addr))
		newThread.start()
		time.sleep(.5)
	except:
		s.close()
		os._exit(1)