import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
import time                 # 시간관련 모듈을 불러옴
from Post import Connect
from multiprocessing import Queue,Lock
from datetime import datetime
from ThermalCamera import Port
from multiprocessing import Pipe

lock = Lock()
class IO():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.Fire_Extinguisher_Flag = False
        self.Fire_OUTPUT = 5
        self.LED1 = 2
        self.LED2 = 6
        self.high_temp_flag = False
        self.spark_flag = False
        self.Port_ = Port()
        self.POST = Connect()
        self.OutputQue = Queue()
        self.signalQue = Queue()
        self.evnet = 0
        self.threshold_temp = 50
        self.degrees = 0
        
    def LED_All_TurnDown(self):
        self.LED_TurnDown(self.Fire_OUTPUT)
        self.LED_TurnDown(self.LED1)
        self.LED_TurnDown(self.LED2)
        
        
    #Led Set Up
    def Led_SetUp(self,LED_pin):
        GPIO.setup(LED_pin, GPIO.OUT)
        
    def pin_SetUp(self,pin):
        GPIO.setup(pin,GPIO.IN)
 
    def LED_TurnUP(self,LED_pin):
        GPIO.output(LED_pin,GPIO.HIGH)
        
    def LED_TurnDown(self,LED_pin):
        GPIO.output(LED_pin,GPIO.LOW)
        
    def Input(self,signal,output,pp):
        try:
            Fire_sensor = 21
            GPIO.setmode(GPIO.BCM) 
            self.pin_SetUp(Fire_sensor)
            global endTime
            global startTime
            self.Led_SetUp(self.LED1)
            self.Led_SetUp(self.LED2)
            self.Led_SetUp(self.Fire_OUTPUT)
            endTime = 0
            startTime=0
            Cur_event= 0
            pre_event = 0
            b_pre_Post_Flag = True
            
            #for debug..
            while True:
                try:
                    # post 파이프라인 연결
                    pp.send(self.POST)
                    
                    self.OutputSignal(output,signal)
                    self.set_event()
                    #################################
                    ###########점화장치 on###########
                    #################################
                    # uppulse
                    #################################
                    ###########점화장치 off###########
                    #################################
                    # downpulse
                    
                    
                    #high temp signal
                    self.high_temp_process()   
                    
                    #이벤트 변경시 녹화신호
                    self.put_signal_Data(signal,Cur_event,pre_event)

                    #Post regular signal
                    b_pre_Post_Flag = self.QuaterPost(b_pre_Post_Flag)
                    Cur_event = pre_event
                except:
                    continue
                 
        finally:
            GPIO.cleanup()
        return

    def set_event(self):
        if not (self.high_temp_flag and self.spark_flag):
            self.POST.event=0
            self.evnet = self.POST.event
            return self.POST.event
        
        elif (not self.high_temp_flag and self.spark_flag):
            self.POST.event=1
            self.evnet = self.POST.event
            return self.POST.event
        
        elif (self.high_temp_flag and not self.spark_flag):
            self.POST.event=2
            self.evnet = self.POST.event
            return self.POST.event
        else:
            self.POST.event=3
            
            return self.POST.event
    
    def OutputSignal(self,output,signal):
        # Thermal 카메라의 데이터 테이블 받아오기
        if not(output.empty()):
            outputData = output.get()
            if(outputData == 10):
                self.Fire_Extinguisher_Flag = True
                print("Fire extinguihser is started!!!!")
                self.Fire_Output(self)
                return 
            if(outputData ==11):
                print("ALL LED is initialized")
                self.LED_All_TurnDown(self)
                return
            else:
                # 열화상 카메라 데이터 출력
                #print(outputData)
                signal.put(1)
                
            # detect Fire 
            # dht-11 고온일 경우로 변경

    def set_status(self):
        if not (self.high_temp_flag and self.spark_flag):
            self.POST.status = 0
            return
        else:
            
            if (self.high_temp_flag or self.spark_flag):
                if(self.high_temp_flag and self.spark_flag):
                    self.POST.status = 2
                    return
                self.POST.status = 1
                return
        
    def Fire_Output(self):
        self.LED_TurnUP(self,self.Fire_OUTPUT)


    def Up_Pulse(current_state,previous_state):
        if(current_state == 1 and previous_state == 0):
            return True
        return False            
        
    def Down_Pulse(current_state,previous_state):
        if(current_state == 0 and previous_state == 1):
            return True
        return False
    
    
  

    # 이벤트가 달라질 경우에 신호보내기
    def put_signal_Data(self,signal,cur_evt,pre_evt):
        if not(cur_evt == pre_evt):
            signal.put(cur_evt)
        return
    
    def QuaterPost(self,b_pre_Post_Flag):
        now = datetime.now()
        strMinute = now.minute
        if(strMinute%5 == 4):
            b_pre_Post_Flag=True
            return b_pre_Post_Flag
        
        elif(strMinute%5 == 0 and b_pre_Post_Flag == True):
            b_pre_Post_Flag=False
            self.POST.sendSignal()
            return b_pre_Post_Flag            
        
        

        
    def high_temp_process(self):
    #fire signal
        global endTime
        global startTime
        # dht-11 온도
        self.POST.temperature=self.degrees
        if (self.degrees >=self.threshold_temp):
            endTime = time.time()                    
            Time = endTime - startTime
            
            if(Time>=0.5):
                self.high_temp_flag = True
                return
                
        else:
            startTime = time.time()
            self.high_temp_flag = False
            return
    print("GPIO Loading complete")    