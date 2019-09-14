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
	messageCount = 0
	stopped = False
	def recieve(self, c, addr):
		try:
			self.clientObj=c
			self.clientAddr=addr
			self.clientObj.send('Username: '.encode())
			incomingName = self.clientObj.recv(430).decode()
			duplicates = 0
			if len(clients)>=1:
				for client in clients:
					testName = client.username
					if testName.endswith('}') and testName[-3]=='{':
						testName = testName[:-3]
					if incomingName == testName:
						duplicates += 1
			if duplicates>0:
				incomingName = incomingName+'{'+str(duplicates)+'}'
			self.username = incomingName
			self.clientObj.send('Username set'.encode())
			clients.append(self)
			sendAll("Connection from: {}({})".format(addr[0],self.username))
		except:
			self.stopped = True
			
		while True:
			if self.stopped:
				break
			try:
				rawMess = self.clientObj.recv(1024)
				rawMess = str(rawMess)
				if rawMess.find('\\x08') != -1:
					rawMess = rawMess.split('\\x08')
					incomingMess = ''
					for i in range(len(rawMess)):
							incomingMess = incomingMess[:-1]+rawMess[i]
					incomingMess = incomingMess[2:-1]
				else:
					incomingMess = rawMess[2:-1]
				if incomingMess != '' and self.messageCount < 11:
					sendAll("{}({}): {}".format(self.clientAddr[0], self.username, incomingMess))
					self.messageCount += 1
			except (ConnectionResetError, ConnectionAbortedError):
				sendAll(">{}({}) has disconnected".format(self.clientAddr[0], self.username))
				break
			except BrokenPipeError:
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

def messagesPerMinute():
	while True:
		if len(clients)>0:
			for client in clients:
				client.messageCount = 0
		time.sleep(30)
	
#Create socket
s = socket.socket()
s.bind(('', 1245))
s.listen()
print('Server Online')
print('')

thread = threading.Thread(target=messagesPerMinute)
thread.start()

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