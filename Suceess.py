import cv2
import numpy as np          # openCV
import socket, time         # 소켓,타임
import struct

 # Frame 설정 
global buf_size
global chunkSize
def TcpServer(host,port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP 소켓 객체 생성
    return server_socket
#Tcp Connecting 
def Connect(host,port):
    server_socket = TcpServer(host,port)
    server_socket.bind((host, port))
    server_socket.listen()
    connectionSocket,addr = server_socket.accept();                 # 소켓 및 IP 반환
    print("Client_Info:",str(addr))
     # set Buffer size 
    buf_size = 1024*1024*1                 # Buffer Size is free (1Mb)
    connectionSocket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,buf_size)
    return connectionSocket
def Fps(Time,img):
    FPS = round(1/Time,0)
    red = (0,0,255)
    font = cv2.FONT_HERSHEY_PLAIN
    img = cv2.putText(img,"FPS:"+str(FPS),(0,25),font,2,red,1, cv2.LINE_AA)

    return img
        
# Mat Data 뿌리기   
def recv_MatData(connectionSocket):
    chunkSize=1024
    #빅 에디안 순으로 데이터 정리  -> 리틀 에디안 순으로 정리
    try:
        start = time.time()         #Fps 계산
        size_data = connectionSocket.recv(4)                #size_data = b''
        size = struct.unpack("<L", size_data)[0]            #size = integer
        data = b''
        sizeCnt=0
        while True:
            if(size-(sizeCnt+1024)>0):
                data += connectionSocket.recv(chunkSize)
                sizeCnt=len(data)
            else:
                chunkSize = size-sizeCnt
                data+=connectionSocket.recv(chunkSize)
                sizeCnt=len(data)
            if(sizeCnt>=size):
                break
    except:
        print("데이터가 없습니다. 연결을 재시도하시오.")
        return False
    try:
        # decompress data
        decompressed_data = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), -1)
        # convert decompressed data into cv2 Mat object
        img = cv2.cvtColor(decompressed_data, cv2.COLOR_RGB2BGR)
        end = time.time()   #Fps계산
        Time = end-start
        Fps(Time,img)
        # Display the image
        cv2.imshow('image', Fps(Time,img))
        if cv2.waitKey(10) == ord('s'): #s누르면 정지
            cv2.destroyAllWindows()
            return False
        return True
    except:
        print("이미지 변환 실패")
        return False
        
def main(): #Main Start!!
    host = '192.168.10.129'
    port = 6000;
    connectionSocket = Connect(host,port)
    while(recv_MatData(connectionSocket)):
        recv_MatData(connectionSocket)
    connectionSocket.close()        
    try:
        server_socket=TcpServer
        TcpServer.close()
    except:
        print("socket_close_err")
if __name__=="__main__":#main 실행하기
    main()
