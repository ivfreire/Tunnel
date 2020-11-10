'''

	Created by Ícaro Freire on 22th October 2020.
	São Paulo, BR.

'''

import socket
from threading import Thread
import importlib
import sniffer
import sys


FLAGS = {
	'start':	('localhost', 25565),
	'end':		None,
	'log_path':	None
}


class Receiver(Thread):
	def __init__(self, host, port, n=1, title='Receiver', id=0):
		super().__init__(None, self)
		self.host		= host
		self.port		= port
		self.n			= n
		self.title		= title
		self.sock		= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients	= []
		self.id			= id
		return
    
	def run(self):
		try:
			self.sock.bind((self.host, self.port))
			self.sock.listen(self.n)
			print('{} is now listening on {}:{}'.format(self.title, self.host, self.port))
		except Exception as e:
			print('Exception: {}'.format(e))
			return
		
		self.accept_thread = Thread(target=self.accept)
		self.accept_thread.start()

		while self.is_alive:
			for client in self.clients:
				data = client[0].recv(1024)
				if data != b'':
					importlib.reload(sniffer)
					data = sniffer.sniff(data, source='R', id=self.id)
					self.sender.send(data)
					

		self.accept_thread.join()

		return

	def accept(self):
		while len(self.clients) < self.n:
			conn, addr = self.sock.accept()
			self.clients.append((conn, addr))
			print('{} has connected to {}.'.format(str(addr), self.title))
		return
    
	def send(self, data, encoding='UTF-8'):
		data = bytes(str(data).encode(encoding))
		for client in self.clients:
			client[0].send(data)
		return
    
	def close(self):
		self.sock.close()
		return

class Sender(Thread):
	def __init__(self, host, port, title='Sender', sniffer=None, id=0):
		super().__init__(None, self)
		self.host		= host
		self.port 		= port
		self.title		= title
		self.sock		= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.is_ready	= False
		self.id			= id
		self.sniffer	= sniffer
		return
    
	def run(self):
		try:
			self.sock.connect((self.host, self.port))
			print('{} has connected to {}!'.format(self.title, self.host))
		except Exception as e:
			print('Exception: {}'.format(e))
			return

		while self.is_alive:
			data = self.sock.recv(1024)
			if data != b'':
				for client in self.clients:
					importlib.reload(sniffer)
					data = sniffer.sniff(data, source='S', id=self.id)
					client[0].send(data)

		return
    
	def send(self, data, encoding='UTF-8'):
		data = str(data).encode(encoding)
		self.sock.send(data)
		return
    
	def close(self):
		self.sock.close()
		return

class Tunnel(Thread):
	def __init__(self, begin=('127.0.0.1', 3000), end=('127.0.0.1', 3001), sniffer=None, log_path=None, id=0):
		super().__init__(None, self)
		self.receiver   = Receiver(begin[0], begin[1], 1, 'Receiver {}'.format(id), id=id)
		self.sender     = Sender(end[0], end[1], 'Sender {}'.format(id), id=id)
		return

	def run(self):
		self.receiver.sender	= self.sender.sock
		self.sender.clients		= self.receiver.clients

		try:
			self.receiver.start()
			self.sender.start()
		except Exception as e:
			print('Exception: {}'.format(e))

		self.receiver.join()
		self.sender.join()
		return

	def close(self):
		self.sender.close()
		self.receiver.close()

def treat_address(addr):
	n_addr = str(addr).split(':')
	if len(n_addr) == 1: n_addr += [25565]
	else: n_addr[1] = int(n_addr[1])
	return tuple(n_addr)

def main():
	for i in range(len(sys.argv)):
		if (sys.argv[i] == '-t') or (sys.argv[i] == '--target'):
			FLAGS['end'] = treat_address(sys.argv[i+1])
		if sys.argv[i] == '-w':
			FLAGS['log_path'] = sys.argv[i+1]

	if FLAGS['end'] == None: return

	tunnel = Tunnel(FLAGS['start'], FLAGS['end'], log_path=FLAGS['log_path'])
	tunnel.start()
	return

if __name__ == '__main__':
	main()