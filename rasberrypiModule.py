from CameraRecord import Camera                 # Camera Class
#from Database import DatabaseClass              # Database Class
from Detect_fire import Detection
import cv2
import time
import atexit # program close
from multiprocessing import Pool,Process,Queue
from multiprocessing import Lock
import numpy as np          # openCV
from datetime import datetime
#from GPio import IO
from Character import Char
from ServerData import Data
from Pipe import pipe
import os
import signal
import queue as q
import threading
import pickle
Detect = Detection()
svData = Data()
cam = Camera()
#IO_ = IO()
GUI = Char()
#Signal = IO_.signalQue
#outputQue = IO_.OutputQue

# connect Pipe Line
pp = pipe()
pp_thermal = pipe()

# create q
post_pipe_q = q.Queue()

# create record pipe q
record_pipe_q = q.Queue()

# this frmae is for detect fire
detect_q = Queue()

def main():
    global cam
    global bCameraOn
    global frame
    global CameraProcess
    global SensorProcess
    global ServerDataProcess
    global ThermalCameraProcess
    global detect_process
    cap = cv2.VideoCapture(0)
    #cap = cam.Camera_Start(cap)
    #if program is abnormally or normally closed
    signal.signal(signal.SIGINT, exit_handler)
    atexit.register(exit_handler,signal)
    bCameraOn = False
    cam.bRecordQue = True
    Signal = Queue()
    CameraProcess = Process(target=Camera_Start_,args=([Signal,pp,cap,detect_q]))
    #SensorProcess = Process(target =IO_.Input,args=(Signal,outputQue,pp,pp_thermal,))
    #ServerDataProcess = Process(target = svData.Data_Loop,args = (outputQue,))
    #ThermalCameraProcess = Process(target = IO_.Port_.Thermal_Loop,args=(pp_thermal,))
    detect_process = Process(target=Detect.run,args = ([cap,detect_q]))
    CameraProcess.start()
    #SensorProcess.start()
    #ServerDataProcess.start()
    #ThermalCameraProcess.start()
    detect_process.start()
    CameraProcess.join()
    #SensorProcess.join()
    #ServerDataProcess.join()
    #ThermalCameraProcess.join()
    detect_process.join()

def exit_handler(self,bsignal):
    global src
    global CameraProcess
    global SensorProcess
    global ServerDataProcess
    global ThermalCameraProcess
    global detect_process
    print('program will be closing')
    if CameraProcess.is_alive():
        CameraProcess.terminate()
        CameraProcess.join()
        print('Camera Process is closed')
    
    if SensorProcess.is_alive():
        SensorProcess.terminate()
        SensorProcess.join()
        print('Sensor Process is closed')
    
    # if ServerDataProcess.is_alive():
    #     ServerDataProcess.terminate()
    #     ServerDataProcess.join()
    #     print('ServerDataProcess is closed')
    
    if ThermalCameraProcess.is_alive():
        ThermalCameraProcess.terminate()
        ThermalCameraProcess.join()
        print('ThermalCameraProcess is closed')
    if detect_process.is_alive():
        detect_process.terminate()
        detect_process.join()
        print('detect_process is closed')
    if cam.src is not None:
        cam.src.release()
        print('Camera is closed')
    
    if svData.Socket is not None:
        svData.Socket.close()
    print("TCP Socket is closed")
    
    
    
    print("Program Close is successed")
    return
    

def Camera_Start_(Signal,pp,cap,detect_q):
    
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
    src= cap
    
    now = datetime.now()
    strTime = now.strftime('%Y_%m_%d_%H_%M_%S')
    #Camera Setting!
    
    #post = pp.receive()
    # if Turn on Take a picture
    status,frame = src.read()
    
    post = None
    cam.CaptureImage(strTime,frame,post,"image")
        
    if(cam.openCam):
        bCameraOn =True
        bRecordStart = False
        print("Camera Start")
        post_pipe_thread = threading.Thread(target=post_pp_q,args=())
        post_pipe_thread.start()
        
       
        
        while(bCameraOn):
            # try:
            # Time initial per Thread tic
                now = datetime.now()
                strTime = now.strftime('%Y_%m_%d_%H_%M_%S')
                strMinute = now.minute
                #query Camera status , frame
                status,frame = src.read()
                
                # if status is normal
                if status:
                        
                    # this frame is for detect fire so you can save 5 frame at once
                    cam.detect_frame(frame,detect_q)
                    
                     
                    try:
                        if not(post_pipe_q.empty()):
                            post =pickle.loads(post_pipe_q.get())
                    except:
                        print("post doesn't operate")
                        continue
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
                    if (strMinute % 15 == 14):
                        bCaptureFlag = True
                    
                    if (strMinute % 15 ==  0 and bCaptureFlag == True and not bRecord):
                        bCaptureFlag = False
                        cam.CaptureImage(strTime,frame,post,"image")
                        print("Capture and Post")    
                                        
                    if(bRecordStart):
                        bRecord = True
                        bRecordStart=False
                        # set time three sencond 
                        p=cam.RecordTS_Start("3",post,startTime,set_time)
                        
                        # show flag status
                        GUI.progressbar_Start(set_time)
                    #Record Video
                    if(bRecord):
                        endTime = time.time()
                        Time = endTime-startTime
                        #show flag status in progressbar
                        GUI.show_progressbar(Time,set_time)
                        #Record start
                        cam.RecordTS(p,frame,post)    
                        continue
                    startTime = time.time()
                    endTime = time.time() 
                    
         
            # except:
            #     print("cam_err")
            #     continue               
            
    else:
        bCameraOn = False
        str = "Cam is not opend\n please check your camera status"
        cam.Log_Write(str,strTime)

    return



def post_pp_q():
    try:
        while True:
            post = pp.receive()
            #객체를 시리얼화
            serialized_post = pickle.dumps(post)
            post_pipe_q.put(serialized_post)
    except:
        print("Post thread has err")

if __name__=="__main__":#main 실행하기
    main()
