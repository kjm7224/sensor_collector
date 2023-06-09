#import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
import time                 # 시간관련 모듈을 불러옴
from Post import Connect
from multiprocessing import Queue,Lock
from datetime import datetime
from ThermalCamera import Port
from multiprocessing import Pipe
from dht_11 import dht_11
import queue as q
import threading

lock = Lock()
class IO():
    def __init__(self):
        
        self.dht_11 = dht_11()
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
        self.event = "0"
        self.threshold_temp = 500
        self.degrees = 0
        self.humidity = 0
        self.q_degree = q.Queue()
        
        #spark
        self.cur_spark_flag = 0
        self.pre_spark_flag = 0
        
        
        #for thermal cam debug
        self.thermal_cam_cur_flag = False
        self.thermal_cam_pre_flag = False
    def Input(self,signal,output,pp,pp_thermal):
        try:
            Fire_sensor = 20
            GPIO.setmode(GPIO.BCM) 
            self.pin_SetUp(Fire_sensor)
            global endTime
            global startTime
            self.Led_SetUp(self.LED1)
            self.Led_SetUp(self.LED2)
            self.Led_SetUp(self.Fire_OUTPUT)
            endTime = 0
            startTime=0
            Cur_event= '0'
            pre_event = '0'
            b_pre_Post_Flag = True
            dht_11_thread = threading.Thread(target=self.dht_11_loop,args=())
            dht_11_thread.start()
            #for debug..
            while True:
                try:
                    Cur_event = self.event
                    
                    # post 파이프라인 연결
                    pp.send(self.POST)
                    #열화상 데이터 수신
                    self.thermal_process(pp_thermal,signal,pp)
                    # 화재 진압 트리거 신호
                    self.OutputSignal(output,signal)
                    # 이벤트 설정
                    self.set_event()
                    # if 이벤트 != 0,녹화,continue
                    self.set_record(signal)
                    # 온도 센서 받아오기 -> Q
                    self.get_degree()
                    # 불꽃 감지 센서 받아오기
                    self.get_spark(Fire_sensor)

                    
                    # 온도 센서 일정 온도 이상시 이상 플래그  on
                    self.high_temp_process()   
                    
                    #이벤트 변경시 녹화신호
                    self.put_signal_Data(signal,Cur_event,pre_event)

                    # #Post regular signal
                    # b_pre_Post_Flag = self.QuaterPost(b_pre_Post_Flag)
                    # pre_event = Cur_event
                except:
                    print("sensor_err")
                    continue
                    
        finally:
            GPIO.cleanup()
        return        
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
    
    def dht_11_loop(self):
        while True:
            try:
                humidity,degrees = self.dht_11.q_dht()
                degrees = round(degrees,1)
                humidity = round(humidity,1)
                self.q_degree.put([degrees,humidity])
                
            except:
                continue
    def get_degree(self):        
        if not (self.q_degree.empty()):
            ntemp = self.q_degree.get()
            self.degrees = ntemp[0]
            self.humidity = ntemp[1]
            print(ntemp[0],ntemp[1])
        return
    
    def get_spark(self,pin):
        self.pre_spark_flag = self.cur_spark_flag
        self.cur_spark_flag = GPIO.input(pin)
        if (self.Down_Pulse(self.cur_spark_flag,self.pre_spark_flag)):
            self.spark_flag = True
            self.POST.flame = "1"

        elif(self.Up_Pulse(self.cur_spark_flag,self.pre_spark_flag)):
            self.spark_flag = False
            self.POST.flame = "0"
        return
    

    def thermal_process(self,pp_thermal,signal,pp):
        self.thermal_cam_pre_flag = self.thermal_cam_cur_flag
        
        thermal_cam = pp_thermal.receive()
        self.POST.thermal = thermal_cam[1]
        if(thermal_cam[0]>=500 and thermal_cam[0]<=20000):
            self.thermal_cam_cur_flag = True
        else:
            self.thermal_cam_cur_flag = False
        
        # 열화상 카메라 일정 온도 이상시 녹화
        # if not (self.thermal_cam_cur_flag == self.thermal_cam_pre_flag):
        #     if(self.thermal_cam_cur_flag):
        #         signal.put(1)
        #     else:
        #         signal.put(0)
        
        return
    def set_event(self):
        if (not self.high_temp_flag and not self.spark_flag):
            self.POST.event ="0"
            self.POST.status = "0"
            self.event = self.POST.event
            self.status = self.POST.status
            return self.POST.event
        
        elif (not self.high_temp_flag and self.spark_flag):
            self.POST.event="1"
            self.POST.status="1"
            self.event = self.POST.event
            self.status = self.POST.status
            return self.POST.event
        
        elif (self.high_temp_flag and not self.spark_flag):
            self.POST.event="2"
            self.POST.status="1"
            self.event = self.POST.event
            self.status = self.POST.status
            return self.POST.event
        else:
            self.event = "3"
            self.POST.status = "2"
            self.status = self.POST.status
            self.POST.event="3"
            return self.POST.event
        
    def set_record(self,signal):
        if not (self.event=="0"):
            self.POST.detect_event = self.event
            self.POST.detect_status = self.status
            signal.put(1)
            
        else:
            signal.put(0)
    
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
            # else:
            #     # 열화상 카메라 데이터 출력
            #     print(outputData)
            #     #signal.put(1)
                
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


    def Up_Pulse(self,current_state,previous_state):
        if(current_state == 1 and previous_state == 0):
            return True
        return False            
        
    def Down_Pulse(self,current_state,previous_state):
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
        if(strMinute%15 == 4):
            b_pre_Post_Flag=True
            return b_pre_Post_Flag
        
        elif(strMinute%15 == 0 and b_pre_Post_Flag == True):
            b_pre_Post_Flag=False
            self.POST.sendSignal()
            return b_pre_Post_Flag            
        
        

        
    def high_temp_process(self):
    #fire signal
        global endTime
        global startTime
        # dht-11 온도
        self.POST.temperature=self.degrees
        self.POST.humidity = self.humidity
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

