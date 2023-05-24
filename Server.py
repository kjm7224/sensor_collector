import socket
import subprocess

class Data():
    def __init__(self):
        self.IP_ADDRESS = subprocess.check_output(['hostname', '-I']).decode().strip()
        self.PORT = 8001
        self.Socket = None
        
    def Connect(self):
        self.Socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.Socket.bind((self.IP_ADDRESS,self.PORT))
        self.Socket.listen(1)
        return self.Socket

    def Data_Loop(self,output):
        self.Socket =Data.Connect(self)
        while True:
            connectionSocket, addr = self.Socket.accept()
            print("Client_Info:",str(addr))
            while True:
                data = connectionSocket.recv(2)
                data = data.decode("utf-8")
                if(data=="10"):
                    output.put(10)
                
                elif(data=="11"):
                    output.put(11)

print("TCP Loading complete ")