import socket
import threading
import time
import os
import msvcrt as m
from Cryptodome import Random
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP as PK
from Cryptodome.Cipher import AES
import base64

global connections
global sendTargets
global IOHandle
connections = []
sendTargets = []
		
def mainInterface(myName):
	global connections
	global sendTargets
	global IOHandle
	while True:
		useIn = IOHandle.input()
		if useIn.startswith('-'):
			if useIn.startswith('-connect '):
				useIn = useIn.split(' ')
				if len(useIn)==3:
					outgoingClient = outgoingConnection(myName)
					addr = (useIn[1], useIn[2])
					newThread = threading.Thread(target=outgoingClient.connect, args=(addr))
					newThread.start()
				else:
					flashMessage('>>Invalid Number of arguements')
							
			elif useIn.startswith('-list'):
				print('>>CURRENT CONNECTIONS:')
				i=0
				for connection in connections:
					print("[{}]: {}({})".format(i, connection.addr[0], connection.username))
					i+=1
				print()
				print('>>CURRENTLY SENDING TO:')
				i=0
				for connection in sendTargets:
					print("[{}]: {}({})".format(i, connection.addr[0], connection.username))
					i+=1
				print()
				
			elif useIn.startswith('-a '):
				useIn = useIn.split(' ')
				try:
					for target in useIn[1:]:
						target = int(target)
						sendTargets.append(connections[target])
						print('[+]Now sending to connection '+str(target))
				except ValueError:
					flashMessage('>>Invalid Arguement')
				except IndexError:
					flashMessage('>>Connection not found')
					
			elif useIn.startswith('-r '):
				useIn = useIn.split(' ')
				try:
					newTargets = sendTargets
					for target in useIn[1:]:
						target = int(target)
						newTargets[target] = ''
					newNewTargets = newTargets
					i=0
					for target in newTargets:
						if target=='':
							del newNewTargets[i]
							print('[-]No longer sending to connection '+str(i))
						i+=1
					sendTargets = newNewTargets
				except ValueError:
					flashMessage('>>Invalid Arguement')
				except IndexError:
					flashMessage('>>Connection not found')
					
			elif useIn.startswith('-d '):
				useIn = useIn.split(' ')
				try:
					for target in useIn[1:]:
						target = int(target)
						connections[target].stop()
					pruneConnections()
				except ValueError:
					flashMessage('>>Invalid Arguement')
				except IndexError:
					flashMessage('>>Connection not found')

		else:
			if len(sendTargets)>0:
				sendAll(useIn, sendTargets)
			else:
				flashMessage('>>Not sending to any targets')

def handleRecieve(myName):
	while True:
		s = socket.socket()
		# with 
		port = 1245
		bound = False
		while not bound:
			try:
				s.bind(('', port))
				bound = True
			except OSError:
				bound = False
				port += 1
		s.listen()
		print('>>Client Online, port '+str(port))
		print('')
		while True:
			c, addr = s.accept()
			try:
				incomingClient = incomingConnection(myName)
				newThread = threading.Thread(target=incomingClient.handleConnection, args=(c, addr))
				newThread.start()
				time.sleep(.5)
			except Exception as e:
				print('>>Error: '+str(e)+'. Restarting reciever')
				s.close()
				break

# def createConfig():
	# try:
		# os.mkdir('')
	
#Send to all connected clients
def sendAll(outgoing, targets):
	print('(You): '+outgoing)
	for connection in targets:
		try:
			connection.send(outgoing)
		except(ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
			connection.stopped = True
			pass
	pruneConnections()
		
def flashMessage(message):
	print(message, end='', flush=True)
	time.sleep(.08*len(message))
	print('\r'+' '*len(message), end='\r', flush=True)
	
def existingConnection(addr):
	existing = False
	for connection in connections:
		if connection.addr == addr:
			existing = True
			break
	return existing
	
def checkDuplicate(targetName, nameList):
	duplicates = 0
	highestNumber = 0
	for name in nameList:
		if name.endswith('}') and name.find('{')!=-1:
			try:
				number = int(name[name.find('{')+1:-1])
				if number>highestNumber:
					highestNumber = number
			except ValueError:
				pass
			name = name[:name.find('{')]
		if name == targetName:
			duplicates += 1
	if duplicates>0 and highestNumber>=duplicates:
		duplicates=highestNumber+1
	return duplicates
	
def cleanMessage(message):
	if message.find('\\x08') != -1:
		message = message.split('\\x08')
		fixedMess = ''
		for i in range(len(message)):
			fixedMess = fixedMess[:-1]+message[i]
	else:
		fixedMess = message
	return fixedMess

#Find any connections that are now stopped and remove them from the active list
def pruneConnections():
	global connections
	global sendTargets
	newConnections = list(connections)
	i=0
	for connection in connections:
		if connection.stopped:
			del newConnections[i]
		i += 1
	connections = newConnections
	newTargets = list(sendTargets)
	i=0
	for connection in sendTargets:
		if connection.stopped:
			del newTargets[i]
		i += 1
	sendTargets = newTargets

class connection:
	global connections
	global IOHandle
	
	def __init__(self, username):
		self.conn=''
		self.addr=''
		self.username = ''
		self.key = ''
		self.myUsername = username
		self.stopped = False

	def recieve(self):
		while not self.stopped:
			try:
				rawMess = self.conn.recv(1024)
				decoded = base64.urlsafe_b64decode(rawMess)
				iv = decoded[:16]
				encrypted = decoded[16:]
				cipher = AES.new(self.key, AES.MODE_CFB, iv)
				decrypted = cipher.decrypt(encrypted)
				decrypted = str(decrypted)[2:-1]
				if decrypted.startswith('MESSAGE '):
					decrypted = decrypted[8:]
					incomingMess = cleanMessage(decrypted)
					if incomingMess != '':
						IOHandle.output("{}({}): {}".format(self.addr[0], self.username, incomingMess))
			except (ConnectionResetError, ConnectionAbortedError):
				IOHandle.output("[-]Disconnected from {}({})".format(self.addr[0], self.username))
				self.stopped = True
				pruneConnections()
				break
			except BrokenPipeError:
				self.stopped = True
				pruneConnections()
				break
	
	def send(self, message):
		message = 'MESSAGE '+message
		iv = Random.new().read(16)
		cipher = AES.new(self.key, AES.MODE_CFB, iv)
		encrypted_msg = cipher.encrypt(str(message).encode())
		outgoingMessage = base64.urlsafe_b64encode(iv + encrypted_msg)
		self.conn.send(outgoingMessage)
		
	#Call pruneConnections after use(excepting specific circumstances)
	def stop(self):
		self.stopped = True
		self.conn.close()

class incomingConnection(connection):
	global connections
	global IOHandle
	
	def handleConnection(self, c, addr):
		try:
			self.conn=c
			self.addr=addr
			
			if existingConnection(addr):
				self.stopped = True
				pruneConnections()
				return
			incomingName = self.conn.recv(55).decode()
			if not incomingName.startswith('NAME '):
				self.stopped = True
				return
			
			incomingName = incomingName[5:]
				
			if incomingName.endswith('}') and incomingName.find('{')!=-1:
				incomingName = incomingName[:incomingName.find('{')]
			usernameList = []
			for connection in connections:
				usernameList.append(connection.username)
			duplicates = checkDuplicate(incomingName, usernameList)
			if duplicates>0:
				incomingName = incomingName+'{'+str(duplicates)+'}'
				
			self.username = incomingName
			self.conn.send(('NAME '+self.myUsername).encode())
			
			publickey = RSA.importKey(self.conn.recv(1024))
			encryptor = PK.new(publickey)
			self.key = Random.new().read(16)
			encrypted = encryptor.encrypt(self.key)
			encodedEncrypted = base64.b64encode(encrypted)
			self.conn.send(encodedEncrypted)
			
			connections.append(self)			
			IOHandle.output("[+]Connection from: {}({})[{}]".format(addr[0], self.username, len(connections)-1))
			self.recieve()
		except (ConnectionResetError, ConnectionAbortedError, ValueError):
			self.stopped = True
		
class outgoingConnection(connection):
	global connections
	global sendTargets
	global IOHandle
	
	def connect(self, *addr):
		try:
			self.addr=addr
			if existingConnection(addr):
				flashMessage('>>Already connected')
				self.stopped = True
				pruneConnections()
				return
			self.conn=socket.create_connection((addr[0], addr[1]))
			self.conn.send(('NAME '+self.myUsername).encode())
			incomingName = self.conn.recv(55).decode()
			if not incomingName.startswith('NAME '):
				self.stopped = True
				return
			incomingName = incomingName[5:]
				
			if incomingName.endswith('}') and incomingName.find('{')!=-1:
				incomingName = incomingName[:incomingName.find('{')]
			usernameList = []
			for connection in connections:
				usernameList.append(connection.username)
			duplicates = checkDuplicate(incomingName, usernameList)
			if duplicates>0:
				incomingName = incomingName+'{'+str(duplicates)+'}'
			self.username = incomingName

			privatekey = RSA.generate(256*8, Random.new().read)
			publickey = privatekey.publickey()
			decryptor = PK.new(privatekey)
			exportedKey = publickey.exportKey(format='PEM')
			self.conn.send(exportedKey)
			
			encodedEncrypted = self.conn.recv(1024)
			decodedEncrypted = base64.b64decode(encodedEncrypted)
			self.key = decryptor.decrypt(decodedEncrypted)
			
			connections.append(self)
			sendTargets.append(self)
			IOHandle.output("[+]Connection to: {}({})[{}]".format(self.addr[0], self.username, len(connections)-1))
			self.recieve()
		except socket.gaierror:
			flashMessage('>>Invalid arguement')
		except (ConnectionRefusedError, TimeoutError, ConnectionResetError, ConnectionAbortedError):
			print('[-]Error connecting to {}:{}'.format(self.addr[0], self.addr[1]))
			self.stopped = True
	
# Custom IO Handler
# Using input(), if you recieve a message while typing, it will be interuptted and split across multiple lines
# To cicumvent this issue, the intented string is assembled as you type
# When a message is recieved, what you are typing is erased, overwritten by the incoming message, and printed the next line down
# Once you are done typing, the message is erased, because it is then printed by sendAll() with added formatting(or not printed in the case of commands)
class handleIO:
	outbound = ''
	
	def input(self):
		self.outbound = ''
		key = ''
		while key != '\r':
			try:
				key = m.getch().decode()
			except UnicodeDecodeError:
				key=''
			m.getch()
			if key != '\r':
				if key == '\x08':
					if len(self.outbound)>0:
						print('\x08 \x08', end='', flush=True)
						self.outbound = self.outbound[:-1]
				else:
					print(key, end='', flush=True)
					self.outbound = self.outbound+key
		print('\r', end='', flush=True)
		print(' '*len(self.outbound), end='\r', flush=True)
		sending = self.outbound
		self.outbound = ''
		return sending
	
	def output(self, message):
		print('\r', end='', flush=True)
		if len(message)<len(self.outbound):
			print(' '*len(self.outbound), end='\r', flush=True)
		print(message)
		print(self.outbound, end='', flush=True)
		
if __name__ == "__main__":
	os.system("title Decentralized Encrypted Communication Client")
	IOHandle = handleIO()
	# try:
		# with open(os.environ['appdata']+'\\'
	username = input('Username: ')
	reciever = threading.Thread(target=handleRecieve, args=(username,))
	reciever.start()
	sender = threading.Thread(target=mainInterface, args=(username,))
	sender.start()