from CameraRecord import Camera                 # Camera Class
from Database import DatabaseClass              # Database Class
import cv2
import time
#import RPi.GPIO_ as GPIO_     # 라즈베리파이 GPIO_ 관련 모듈을 불러옴
import atexit # program close
from multiprocessing import Pool,Process,Queue
from multiprocessing import Lock
import numpy as np          # openCV
from datetime import datetime
from GPio import IO
from Character import Char
from ServerData import Data
from Pipe import pipe
import os
import signal
svData = Data()
cam = Camera()
IO_ = IO()
GUI = Char()
Signal = IO_.signalQue
outputQue = IO_.OutputQue

# connect Pipe Line
pp = pipe()

def main():
    global cam
    global bCameraOn
    global frame
    global CameraProcess
    global SensorProcess
    global ServerDataProcess
    global ThermalCameraProcess
    #if program is abnormally or normally closed
    signal.signal(signal.SIGINT, exit_handler)
    atexit.register(exit_handler,signal)
    bCameraOn = False
    cam.bRecordQue = True
    CameraProcess = Process(target=Camera_Start_,args=(Signal,pp,))
    SensorProcess = Process(target =IO_.Input,args=(Signal,outputQue,pp,))
    #ServerDataProcess = Process(target = svData.Data_Loop,args = (outputQue,))
    ThermalCameraProcess = Process(target = IO_.Port_.Thermal_Loop,args=(outputQue,))
    CameraProcess.start()
    SensorProcess.start()
    #ServerDataProcess.start()
    ThermalCameraProcess.start()
    CameraProcess.join()
    SensorProcess.join()
    #ServerDataProcess.join()
    ThermalCameraProcess.join()

def exit_handler(self,bsignal):
    global src
    global CameraProcess
    global SensorProcess
    global ServerDataProcess
    global ThermalCameraProcess
    print('program will be closing')
    if CameraProcess.is_alive():
        CameraProcess.terminate()
        CameraProcess.join()
        print('Camera Process is closed')
    
    if SensorProcess.is_alive():
        SensorProcess.terminate()
        SensorProcess.join()
        print('Sensor Process is closed')
    
    if ServerDataProcess.is_alive():
        ServerDataProcess.terminate()
        ServerDataProcess.join()
        print('ServerDataProcess is closed')
    
    if ThermalCameraProcess.is_alive():
        ThermalCameraProcess.terminate()
        ThermalCameraProcess.join()
        print('ThermalCameraProcess is closed')
    
    if cam.src is not None:
        cam.src.release()
        print('Camera is closed')
    
    if svData.Socket is not None:
        svData.Socket.close()
    print("TCP Socket is closed")
    
    
    
    print("Program Close is successed")
    return
    

def Camera_Start_(Signal,pp):
    
    global cam
    global bCameraOn
    global bRecord
    global src
    signalData = 0
    bRecord = False
    bCaptureFlag = False
    bRecordStart = True
    startTime = 0
    endTime = 0
    set_time = 180
    
    
    now = datetime.now()
    strTime = now.strftime('%Y_%m_%d_%H_%M_%S')
    #Camera Setting!
    src = cam.Camera_Start()
    
    # if Turn on Take a picture
    status,frame = src.read()
    cam.CaptureImage(strTime,frame)
    if(cam.openCam):
        bCameraOn =True
        bRecordStart = False
        print("Camera Start")
        while(bCameraOn):
                
            # Time initial per Thread tic
                post = pp.receive()
                now = datetime.now()
                strTime = now.strftime('%Y_%m_%d_%H_%M_%S')
                strMinute = now.minute
                #query Camera status , frame
                status,frame = src.read()
                
                # if status is normal
                if status:
                    
                    # # signal decode
                    if not(Signal.empty()):
                        signalData = Signal.get()
                        
                        if (not bRecord and signalData == 1):              #spark signal
                            bRecordStart = True 
                            time.sleep(0.1)
                            startTime = time.time()
                            
                    if(signalData == 0):
                        Time = endTime-startTime
                        # video flag set 3 minute  
                        if(Time>=set_time):
                            bRecord = False
                            print("Recording video is stop")
                                                                                                   
                    #Capture processing
                    if (strMinute % 5 == 4):
                        bCaptureFlag = True
                    
                    if (strMinute % 5 ==  0 and bCaptureFlag == True):
                        bCaptureFlag = False
                        cam.CaptureImage(strTime,frame)

                    
                    if(bRecordStart):
                        bRecord = True
                        bRecordStart=False
                        # set time three sencond 
                        p=cam.RecordTS_Start("3",post)
                        
                        # show flag status
                        GUI.progressbar_Start(set_time)
                    #Record Video
                    if(bRecord):
                        endTime = time.time()
                        Time = endTime-startTime
                        #show flag status in progressbar
                        GUI.show_progressbar(Time,set_time)
                        #Record start
                        cam.RecordTS(p,frame)    
                        continue
                    startTime = time.time()
                    endTime = time.time()    
                        
        
                continue               
            
    else:
        bCameraOn = False
        str = "Cam is not opend\n please check your camera status"
        cam.Log_Write(str,strTime)

    return
    

if __name__=="__main__":#main 실행하기
    main()
