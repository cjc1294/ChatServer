import socket
import threading
import os
import sys

#Function for recieveing messages from the server
def recieve():	
	try:
		while True:
			incoming = s.recv(1024).decode()
			if incoming != '':
				print (incoming)
	except ConnectionResetError:
		print("Disconnected from server")
		os.execl(sys.executable, sys.executable, * sys.argv)

#Function for sending messages to the server
def send():
	while True:
		mess=input()
		s.send(mess.encode())

#Create socket
s = socket.socket()

#Connect to the inputted server
connected = False
while not connected:
	servIP=input("Server IP: ")
	servPort=input("Port: ")
	try:
		if servIP == "":
			print("Connecting to 192.168.1.10")
			s.connect(('192.168.1.10', int(servPort)))
			connected = True
		else:
			print("Connecting to "+servIP)
			s.connect((servIP, int(servPort)))
			connected  = True
	except ConnectionRefusedError:
		print("Error connecting")
mess = ''
print ("Connected")
print ("")
#Start threads for sending and recieveing
recieveing = threading.Thread(target=recieve)
recieveing.start()
sending = threading.Thread(target=send)
sending.start()