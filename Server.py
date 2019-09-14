import socket
import threading
import time
import os

global s
global clients
clients = []

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
		
def checkDuplicate(name):
	duplicates = 0
	highestNumber = 0
	for client in clients:
		testName = client.username
		if testName.endswith('}') and testName.find('{')!=-1:
			try:
				number = int(testName[testName.find('{')+1:-1])
				if number>highestNumber:
					highestNumber = number
			except ValueError:
				pass
			testName = testName[:testName.find('{')]
		if name == testName:
			duplicates += 1
	if duplicates>0 and highestNumber>=duplicates:
		duplicates=highestNumber+1
	return duplicates
	
class NewClient:
	global clients
	
	def __init__(self):
		self.clientObj=''
		self.clientAddr=''
		self.username = ''
		self.messageCount = 0
		self.stopped = False

	def recieve(self, c, addr):
		try:
			self.clientObj=c
			self.clientAddr=addr
			self.clientObj.send('Username: '.encode())
			incomingName = ''
			while not incomingName.startswith('MESSAGE '):
				incomingName = self.clientObj.recv(450).decode()
			incomingName = incomingName[8:]
			charles = 'We Charles, by the Grace of God King of Sweden, the Goths and the Vends, Grand Prince of Finland, Duke of Scania, Estonia, Livonia and Karelia, Lord of Ingria, Duke of Bremen, Verden and Pomerania, Prince of Rugen and Lord of Wismar, and also Count Palatine by the Rhine, Duke in Bavaria, Count of ZweibruckenKleeburg, as well as Duke of Julich, Cleve and Berg, Count of Veldenz, Spanheim and Ravensberg and Lord of Ravenstein'
			if incomingName != charles:
				incomingName = incomingName[:50]
			if incomingName.endswith('}') and incomingName.find('{')!=-1:
				incomingName = incomingName[:incomingName.find('{')]
			duplicates = checkDuplicate(incomingName)
			if duplicates>0:
				incomingName = incomingName+'{'+str(duplicates)+'}'
			self.username = incomingName
			self.clientObj.send('Username set'.encode())
			clients.append(self)
			sendAll("Connection from: {}({})".format(addr[0],self.username))
		except (ConnectionResetError, ConnectionAbortedError):
			self.stopped = True
		except Exception as e:
			print(e)
			self.stopped = True
			
		while True:
			if self.stopped:
				break
			try:
				rawMess = self.clientObj.recv(1024)
				rawMess = str(rawMess)
				rawMess = rawMess[2:-1]
				if rawMess.startswith('MESSAGE '):
					rawMess = rawMess[8:]
					if rawMess.find('\\x08') != -1:
						rawMess = rawMess.split('\\x08')
						incomingMess = ''
						for i in range(len(rawMess)):
								incomingMess = incomingMess[:-1]+rawMess[i]
					else:
						incomingMess = rawMess
					if incomingMess != '' and self.messageCount < 11:
						sendAll("{}({}): {}".format(self.clientAddr[0], self.username, incomingMess))
						self.messageCount += 1
			except (ConnectionResetError, ConnectionAbortedError):
				sendAll(">{}({}) has disconnected".format(self.clientAddr[0], self.username))
				break
			except BrokenPipeError:
				break
	
if __name__ == "__main__":
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