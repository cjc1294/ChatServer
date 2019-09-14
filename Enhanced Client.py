# -*- coding: utf-8 -*-
import socket
import threading
import os
import sys
from time import sleep
import msvcrt as m

global messages
global outbound
messages = []
global s
outbound = ''
# os.system('color a')
			
def recieving():
	try:
		while True:
			incomingMessage = (s.recv(1024).decode())
			print('\r', end='', flush=True)
			if len(incomingMessage)<len(outbound):
				print(' '*len(outbound), end='\r', flush=True)
			print(incomingMessage)
			print(outbound, end='', flush=True)
	except (ConnectionResetError, ConnectionAbortedError):
		print('Disconnected from server')

def sending():
	global outbound
	while True:
		outbound = ''
		key = ''
		while key != '\r':
			try:
				key = m.getch().decode()
			except UnicodeDecodeError:
				key=''
			m.getch()
			if key != '\r':
				if key == '\x08':
					if len(outbound)>0:
						print('\x08', end='', flush=True)
						print(' ', end='', flush=True)
						print('\x08', end='', flush=True)
						outbound = outbound[:-1]
				else:
					print(key, end='', flush=True)
					outbound = outbound+key
		print('\r', end='', flush=True)
		print(' '*len(outbound), end='\r', flush=True)
		s.send((front+outbound).encode())
		outbound = ''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = False
while not connected:
	try:
		ip = input("IP: ")
		port = int(input("Port: "))
		front = 'MESSAGE '
		s.connect((ip,port))
		connected = True
		print('Connected')
		sleep(.5)
		os.system('cls')
	except Exception:
		connected = False
		os.system('cls')
		print('Error connecting to server')

listen = threading.Thread(target=recieving)
listen.start()
speak = threading.Thread(target=sending)
speak.start()
