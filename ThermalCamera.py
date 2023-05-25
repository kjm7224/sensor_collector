import serial.tools.list_ports
import serial
import sys
import time
import os
from Post import Connect
from datetime import datetime
import time
class Port():
    
    def __init__(self):
        self.ports = serial.tools.list_ports.comports()
        self.post = Connect()
        self.index = 0
        self.data_list = [None]*10
        self.data_index = 0
        self.width = 32
        self.data_len = 520
        self.summary_data_len = 24
        self.sensor_temperature = 10
        self.Fire_triger = 500
        self.data_table = ""
        self.prev_data_table =""
        self.cur_Fire_flag = False
        self.pre_Fire_flag = False
        self.pre_regular_flag = False
        self.nData = None
        
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
        print("Find port....")
   
    def connect_port(self,bdRate):
        try:
            #serial open
            com = serial.Serial(self.ports[self.index].device,bdRate)
        except:
            self.ports = serial.tools.list_ports.comports()
            self.index = 0
            com = None
        return com
    
    def initial_sensor(self,pp_thermal):
        
        com = self.connect_port(115200)
        if not(com==None):
            com.write(b'AT+1\r\n')
            while True:
                try:
                    data = com.readline()
                    if(data == b'AT+OK\r\n'):
                        return com
                   
                    elif(data == b'AT+RDY\r\n'):
                        com.write(b'AT+1\r\n')
                    
                    elif(data == b'\r\n'):    
                        com.close()
                        print("port is initilized please wait some seconds")
                        time.sleep(10)
                        self.Thermal_Loop(pp_thermal)
                except:
                    self.Thermal_Loop(pp_thermal)
                    continue
        else:
            time.sleep(1)
            self.Thermal_Loop(pp_thermal)
    def debuging(self):
        for list in self.data_list:
            print(list)
    
    def put_Data(self,arr):
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
                        self.nData = int(result,16)
                        #for debug 
                        #print(nData)
                
                        # #For demo test
                        # if(nData>=self.Fire_triger):
                        #     self.cur_Fire_flag  = True
                        #     if not(self.cur_Fire_flag==self.pre_Fire_flag):
                        # else:
                        #     self.cur_Fire_flag  = False
                        #     if not(self.cur_Fire_flag==self.pre_Fire_flag):
                        #         self.post.send_thermal_cam(0,self.data_table)
                            
                        # self.pre_Fire_flag = self.cur_Fire_flag
        # outputQue.put(self.data_table)
        return
    
    def Thermal_Loop(self,pp_thermal):
        self.find_port()
        com = self.initial_sensor(pp_thermal)
        
        #create 32 by 32 table
        arr = [[0 for x in range(32)] for y in range(32)]
        
        print("thermal camera is opend")
        while True:
            try:
                # insert data in byte array[10]
                data=com.readline()
                self.data_list[self.data_index]=data
                self.data_index +=1
                if(self.data_index >9):
                    self.data_index=0
                if(self.data_index==0):
                    self.put_Data(arr)
                    pp_thermal.send([self.nData,self.data_table])
            except: 
                self.__init__()
                self.find_port()
                com = self.initial_sensor(pp_thermal)
        
                print("Thermal Cam has crutial err")  
                continue  

print("TermalCamera loading complete")

#debug...
# from Pipe import pipe
# Pt = Port()
# pp = pipe
# Pt.Thermal_Loop(pp)