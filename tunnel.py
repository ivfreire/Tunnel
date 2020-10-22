import socket
from threading import Thread

class Receiver(Thread):
	def __init__(self, host, port, n=1, title='Receiver'):
		super().__init__(None, self)
		self.host		= host
		self.port		= port
		self.n			= n
		self.title		= title
		self.sock		= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients	= []
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
	def __init__(self, host, port, title='Sender'):
		super().__init__(None, self)
		self.host		= host
		self.port 		= port
		self.title		= title
		self.sock		= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.is_ready	= False
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
	def __init__(self, begin=('127.0.0.1', 3000), end=('127.0.0.1', 3001), id=0):
		super().__init__(None, self)
		self.receiver   = Receiver(begin[0], begin[1], 1, 'Receiver {}'.format(id))
		self.sender     = Sender(end[0], end[1], 'Sender {}'.format(id))
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

def main():
	tunnel = Tunnel(('localhost', 25565), ('192.168.0.27', 25565))
	tunnel.start()
	return

if __name__ == '__main__':
	main()