import socket
import threading

def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('127.0.0.1',1245))
	while True:
		s.send('MESSAGE ping'.encode())

while True:
	thread = threading.Thread(target=main)
	thread.start()