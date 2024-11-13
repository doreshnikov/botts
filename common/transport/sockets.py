import socket


class SocketTransport:
    CHUNK_SIZE = 512
    
    def __init__(self, conn: socket.socket, marshaller):
        self.conn = conn
        self.marshaller = marshaller

    def send(self, data: object):
        self.conn.send(len(data).to_bytes(8))
        self.conn.send(self.marshaller.dumps(data))
        
    def receive(self) -> object:
        size = int.from_bytes(self.socket.recv(8))
        data = bytes()
        while len(data) < size:
            data += self.socket.recv(SocketTransport.CHUNK_SIZE)
        return self.marshaller.loads(data[:size])