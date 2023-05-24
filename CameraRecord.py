#from Database import DatabaseClass              # Database Class
import cv2
import time
import threading
import numpy as np          # openCV
import queue                # queue
import os
import subprocess
from Post import Connect
from datetime import datetime

Lock = threading.Lock()
Connect_ = Connect()
class Camera():
    #db = DatabaseClass()
    def __init__(self):
        self.m3u8_Name = ""
        global Lock
        self.cnt = 0
        self.strPostdir = ""
        self.strFolderName = ""
        self.strPost_FileName = ""
        self.src = cv2.VideoCapture(0)
        
    Lock = threading.Lock()
    queue = queue.Queue()
    
    def Read_m3u8(self,p,pp):
        
        cnt = 0
        while True:
            try:
                output = p.stderr.readline().decode()
                
                if('.ts' in output):
                    
                    str_m3u8Name = self.strPost_FileName+".m3u8"
                    str_tsName = "{strPostName}{cnt}.ts".format(strPostName=self.strPost_FileName,cnt=cnt)
                    pp.postRequest(self.strFolderName,str_m3u8Name,str_tsName)
                    cnt+=1
            except:
                continue
            
        
    def RecordTS(self,p,frame):
        
        p.stdin.write(frame.tostring())

    def RecordTS_Start(self,setTime,pp):
        self.strFolderName = "Video"
        Camera.CreateFolder(self.strFolderName)
        now = datetime.now()
        Time = now.strftime('%m_%d_%H_%M_%S')
        intTime = int(Time)
        self.m3u8_Name = "Video/"+Time+".m3u8"
        strDir = os.getcwd()
        self.strPostDir = strDir+"/"+self.strFolderName
        self.strPost_FileName = Time
        #str_abs_path = os.path.abspath(__file__)
        cmd = ['ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
       '-s', '640x480', '-pix_fmt', 'bgr24', '-r', '30',
       '-i', '-', '-c:v', 'libx264',
       '-pix_fmt', 'yuv420p', '-preset', 'ultrafast',
       '-f', 'hls', '-hls_time', setTime,
       '-hls_list_size', '3', '-hls_flags', 'delete_segments',
       '-hls_delete_threshold', '1', '-force_key_frames', 'expr:gte(t,n_forced*1)',
       self.m3u8_Name]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
        tempThread = threading.Thread(target=self.Read_m3u8,args=(p,pp,))
        tempThread.start()
        return p
    
    def Record(strTime,fps):
        
        
        now = datetime.now()
        Time = now.strftime('%m_%d_%H_%M_%S')
        intTime = int(Time)
        strDir = os.getcwd()
        strFolderName = "Video"
        fourcc = cv2.VideoWriter_fourcc(*'X264')#Rasberry
        startTime = time.time()
        # because fps is shared resource
        
        #Create Folder
        Camera.CreateFolder(strFolderName)
        strName = strTime+".m3u8"
        strPath = strDir+"/"+strFolderName+"/"+strName
        #Temp dir
        strTempDir = strDir+"/"+strFolderName
        #Write Db
        #Camera.db.insertDB(strTable,"Video",intTime,strName,strPath)
        #Camera.db.commit()
        
        #Write Data.txt
        Camera.Data_Write(strTime,strFolderName,strName,strPath)
        
        #post Data
        Connect_.postRequest(strFolderName,strName,None)
        
        #use opencv video writer
        
        #use ffmpeg video writer
        videoName = strFolderName+"/"+strTime
        ts_videoName = videoName+".ts"
        m3u8_videoName = videoName+".m3u8"
        cmd = ['ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo', '-s', '640x480', '-pix_fmt', 'bgr24', '-r', '30', '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'ultrafast', '-f', 'segment', '-segment_time', setTime, '-segment_format', 'mpegts', '-segment_list', m3u8_Name, '-strftime', '1', 'Video/%Y_%m_%d_%H_%M_%S.ts']
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        while True:
            if (Camera.queue.qsize()>=1):
                dst= Camera.queue.get()
                p.stdin.write(dst.tostring())
                
            else:
                endTime=time.time()
                if(endTime-startTime<=10):
                    continue
                p.stdin.close()
                p.wait()
                
                str = "recording complete"
                print(str)
                Camera.Log_Write(str,strTime)
                break
        return False


    def Camera_Start(self):                         # Camera Setting
        self.src.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.src.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return self.src

    def openCam(src):                           # catch Open Cam
        return src.isOpened()
        
    def PushRecordDataStart(self,strTime,frame,SetTime):
        Time = 0
        #pushData_Thread = threading.Thread(target = Camera.PushData,args =(frame,frame,SetTime,strTime,Time,))
        #pushData_Thread.start()
        str = "Record Start!!"
        global StartTime
        StartTime = time.time()
        print(str)
        Camera.Log_Write(str,strTime)
        Camera.queue.put(frame)
       
        Record_Thread = threading.Thread(target=Camera.Record,args=(strTime,30,))
        Record_Thread.start()
        
    def PushData(self,src,SetTime,strTime,Time):
        if(Time<=SetTime):
            Camera.queue.put(src)
            return True
       
        else:
            str = "Record end"
            Camera.Log_Write(str,strTime)
            print("record end")
            return False
                
        
    def CaptureImage(self,strTime,frame):
        strDir = os.getcwd()
        strFolderName = "Image"
        now = datetime.now()
        Time = now.strftime('%m_%d_%H_%M_%S')
        intTime = int(Time)
        
        # Create Forder
        Camera.CreateFolder(strFolderName)
        strName = strTime+".jpg"
        strPath = strDir+"/"+strFolderName+"/"+strName
        strTempDir = strDir+"/"+strFolderName
        
        #Write Data.txt
        Camera.Data_Write(strTime,"Image",strName,strPath)
        
        
        
        cv2.imwrite(strPath,frame)
        str = "CaptureImage"
        Camera.Log_Write(str,strTime)
        print(str)
        #Post Data
        Connect_.postRequest(strFolderName,strName,None)
        #Set Db
        #Camera.db.insertDB(strTable,"Image",intTime,strName,strPath)
        #Camera.db.commit()
        
    def Data_Write(Time,Foramt,Name,Path):# data Write
        Camera.CreateFolder("DATA")
        f = open("DATA/Data.txt",'a')
        strTemp = Time+"\t"+Foramt+"\t"+Name+"\t"+Path+"\r\n"
        f.write(strTemp)
        f.close()
        return strTemp
    

        
    def Log_Write(strMessage,strTime):#로그 기록
        Camera.CreateFolder("LOG")
        f = open("LOG/Log_Sequence.txt",'w')
        f.write("["+strTime+"]"+strMessage)
        f.close()
    
    def CreateFolder(strName):
        if not os.path.exists(strName):
            os.makedirs(strName)

    def RecordText(frame):
        now = datetime.now()
        strTime = now.strftime('%Y_%m_%d_%H_%M_%S')
        red = (0,0,255)
        font = cv2.FONT_HERSHEY_PLAIN
        Lock.acquire()
        cv2.putText(frame,"Record",(0,25),font,2,red,1, cv2.LINE_AA)
        cv2.putText(frame,strTime,(0,50),font,2,red,1, cv2.LINE_AA)
        Lock.release()
        return frame

    def LiveShow(self,bCameraOn,frame,record):
        # Live 
        if(bCameraOn):
            Lock.acquire()
            Lock.release()
            cv2.imshow("Live",frame)
            return record
        return False

    def RecordShow(self,frame):
        #Record cam
        RecordFrame = Camera.RecordText(frame)
        cv2.imshow("RecordVideo",RecordFrame)
        cv2.waitKey(1)
        
    print("Camera Loading complete")