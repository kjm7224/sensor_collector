import serial.tools.list_ports
import serial
import sys
import time
import os
from Post import Connect
class Port():
    
    def __init__(self):
        self.ports = serial.tools.list_ports.comports()
        self.index = 0
        self.data_list = [None]*10
        self.data_index = 0
        self.width = 32
        self.data_len = 520
        self.summary_data_len = 24
        self.sensor_temperature = 10
        self.Fire_triger = 509
        self.data_table = ""
        self.prev_data_table =""
        self.post = Connect()
        self.cur_Fire_flag = False
        self.pre_Fire_flag = False
    def print_port(self):
        print("there are connected in port some object")
        for port in self.ports:
            print(port.device, port.description, port.manufacturer)

    def find_port(self):
        for port in self.ports:
            if(port.description=="STM32 Virtual ComPort"):
                if(port.manufacturer=="STMicroelectronics"):
                    break
            self.index +=1
            continue
        print("Found your Theraml Camera port")
   
    def connect_port(self,bdRate):
 
        #serial open
        com = serial.Serial(self.ports[self.index].device,bdRate)
        return com
    
    def initial_sensor(self):
        com = self.connect_port(115200)
        com.write(b'AT+1\r\n')
        while True:
            data = com.readline()
            if(data == b'AT+OK\r\n'):
                return com
    def debuging(self):
        for list in self.data_list:
            print(list)
    
    def put_Data(self,arr,outputQue):
        col = 0
        self.data_table=""
        for list in self.data_list:
            if(len(list)==self.data_len):
                for i in range(6,len(list)-4,4):
                    result = list[i:i+4]
                    row = int((i-6)/4)%32
                    nData = int(result,16)
                    arr[col][row] = nData
                    self.data_table += " "+str(nData)
                    if row==31:
                        col+=1
                        self.data_table +="\n"
            if(len(list)== self.summary_data_len):
                for i in range(6,len(list)-4,4):
                    if(i==self.sensor_temperature):
                        result = list[i:i+4]
                        nData = int(result,16)
                        # For demo test
                        if(nData>=self.Fire_triger):
                            self.cur_Fire_flag  = True
                            outputQue.put(1)
                           
                            
                        else:
                            self.cur_Fire_flag  = False
                            outputQue.put(0)
                            
                        self.pre_Fire_flag = self.cur_Fire_flag
        return
    
    def Thermal_Loop(self,outputQue):
        self.print_port()
        self.find_port()
        com = self.initial_sensor()
        
        #create 32 by 32 table
        arr = [[0 for x in range(32)] for y in range(32)]
        while True:
            try:
                # insert data in byte array[10]
                data=com.readline()
                self.data_list[self.data_index]=data
                self.data_index +=1
                if(self.data_index >9):
                    self.data_index=0
                if(self.data_index==0):
                    self.put_Data(arr,outputQue)
            except:
                print("Thermal Cam has crutial err")  
                continue  
               

print("TermalCamera loading complete")

