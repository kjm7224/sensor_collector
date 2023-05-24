from multiprocessing import Pipe
class pipe:
    def __init__(self):
        self.conn1, self.conn2 = Pipe()
        
    def send(self, data):
        self.conn1.send(data)

    def receive(self):
        return self.conn2.recv()