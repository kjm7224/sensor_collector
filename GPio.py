import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
import time                 # 시간관련 모듈을 불러옴
from Post import Connect
from multiprocessing import Queue,Lock
from datetime import datetime
from ThermalCamera import Port
SignalQue = Queue()

lock = Lock()
Connect_ = Connect()
class IO():
    GPIOO = GPIO
    GPIO.setmode(GPIO.BCM) 
    signalQue = Queue()
    OutputQue = Queue()
    def __init__(self):
        self.Fire_Extinguisher_Flag = False
        self.Fire_OUTPUT = 5
        self.LED1 = 2
        self.LED2 = 6
        self.Fire_flag = False
        self.Port_ = Port()
        
    def LED_All_TurnDown(self):
        self.LED_TurnDown(self.Fire_OUTPUT)
        self.LED_TurnDown(self.LED1)
        self.LED_TurnDown(self.LED2)
        
        
    #Led Set Up
    def Led_SetUp(LED_pin):
        GPIO.setup(LED_pin, GPIO.OUT)
        
    def pin_SetUp(self):
        GPIO.setup(self,GPIO.IN)
 
    def LED_TurnUP(self,LED_pin):
        GPIO.output(LED_pin,GPIO.HIGH)
        
    def LED_TurnDown(self,LED_pin):
        GPIO.output(LED_pin,GPIO.LOW)
        
    def Input(self,signal,output):
        try:
            Fire_sensor = 21
            GPIO.setmode(GPIO.BCM) 
            IO.pin_SetUp(Fire_sensor)
            FIRESIGNAL = 1
            global endTime
            global startTime
            IO.Led_SetUp(self.LED1)
            IO.Led_SetUp(self.LED2)
            IO.Led_SetUp(self.Fire_OUTPUT)
            endTime = 0
            startTime=0
            Current_Signal = 0
            pre_Signal = 0
            b_pre_Post_Flag = True
            #initialize Fire edge signal
            
            #for debug..
            while True:
                try:
                    time.sleep(0.1)
                    IO.OutputSignal(self,output)
                    
                    #Fire signal 
                    Current_Signal=IO.signal_Process(self)   
                    IO.put_signal_Data(self,FIRESIGNAL,signal,Current_Signal,pre_Signal)

                    #Post regular signal
                    b_pre_Post_Flag = IO.QuaterPost(self,b_pre_Post_Flag,Current_Signal)
                    pre_Signal = Current_Signal
                except:
                    continue                  
                 
        finally:
            GPIO.cleanup()
        return

    def OutputSignal(self,output):
        if not(output.empty()):
            outputData = output.get()
            if(outputData == 10):
                self.Fire_Extinguisher_Flag = True
                print("Fire extinguihser is started!!!!")
                IO.Fire_Output(self)
                return 
            if(outputData ==11):
                print("ALL LED is initialized")
                IO.LED_All_TurnDown(self)
                return
            
            # detect Fire 
            if(outputData == 1):
                self.Fire_flag=True
                
            if(outputData == 0):
                self.Fire_flag = False

    def Fire_Output(self):
        IO.LED_TurnUP(self,self.Fire_OUTPUT)

    def regular_Signal(self,cur_sig):
        if(cur_sig==0):
            Connect_.sendSignal(0,0,self.Port_.data_table)
        elif(cur_sig==1):
            Connect_.sendSignal(0,1,self.Port_.data_table)
        elif(cur_sig==2):
            Connect_.sendSignal(1,1,self.Port_.data_table)
        print("Post send regular signal")
        
    def Up_Pulse(current_state,previous_state):
        if(current_state == 1 and previous_state == 0):
            return True
        return False            
        
    def Down_Pulse(current_state,previous_state):
        if(current_state == 0 and previous_state == 1):
            return True
        return False
    

  


    def put_signal_Data(self,Data_Index,signal,cur_sig,pre_sig):
    
        if(cur_sig == 1 and pre_sig == 0):
            signal.put(Data_Index)
            Connect_.sendSignal(0,0,self.Port_.data_table)
            Connect_.sendSignal(1,1,self.Port_.data_table)
            #Connect_.sendSignal(1,1)
            
        elif(cur_sig ==1 and pre_sig ==2):
            signal.put(Data_Index)
            Connect_.sendSignal(0,0,self.Port_.data_table)
            Connect_.sendSignal(1,1,self.Port_.data_table)
            #Connect_.sendSignal(2,2)
        elif(cur_sig == 2 and pre_sig == 0):
            signal.put(Data_Index-1)
            Connect_.sendSignal(0,1,self.Port_.data_table)
            Connect_.sendSignal(1,0,self.Port_.data_table)
            #Connect_.sendSignal(3,3)
        elif(cur_sig == 2 and pre_sig == 1):
            signal.put(Data_Index-1)
            Connect_.sendSignal(0,1,self.Port_.data_table)
            Connect_.sendSignal(1,0,self.Port_.data_table)
            #Connect_.sendSignal(4,4)
        return
    def QuaterPost(self,b_pre_Post_Flag,cur_sig):
        now = datetime.now()
        strMinute = now.minute
        if(strMinute%5 == 4):
            b_pre_Post_Flag=True
            return b_pre_Post_Flag
        
        elif(strMinute%5 == 0 and b_pre_Post_Flag == True):
            b_pre_Post_Flag=False
            IO.post_evnet(self,cur_sig)
            return b_pre_Post_Flag            
        
        
    def post_evnet(self,cur_sig):
        if(cur_sig==0):
            Connect_.sendSignal(0,0,self.Port_.data_table)
            return
        elif(cur_sig==1):
            Connect_.sendSignal(0,1,self.Port_.data_table)
            return
        elif(cur_sig==2):
            Connect_.sendSignal(1,1,self.Port_.data_table)
            return
        
    def signal_Process(self):
    #fire signal
        global endTime
        global startTime
        if (self.Fire_flag):
            endTime = time.time()                    
            Time = endTime - startTime
            
            if(Time>=0.5):
                return 1
                
        else:
            startTime = time.time()
            Time = startTime - endTime
            if(Time>=0.5):
                return 2
        return 0
    print("GPIO Loading complete")    
