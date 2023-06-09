from datetime import timezone
import datetime 
import requests         # using post
import os
class Connect():
    def __init__(self):
        self.OK_CONNECT = 200
        self.NG_CONNECT = 400
        self.TIME_OUT = 5
        self.HOST_NAME = "localhost:9999"
        self.data = {}
        self.event = "0"
        self.status = "0"
        self.temperature  = "0"
        self.flame = "0"
        self.humidity = None
        self.thermal = None
        # 초기 이벤트 발생 당시
        self.detect_status = None
        self.detect_event = None
        
        
        
        
        
        
    def requestGet(self):
        url = "http://"+self.HOST_NAME+"/api/info"
        result=requests.get(url,params={"serial":"device_type"})
        print(result.text)        
        print(result.status_code)
    
    def postRequest(self,Format,File_name,m3u8_name,jpg_name):
        
        try:
            self.data = {}
            url = url = "http://"+self.HOST_NAME+"/api/sensor_data"
            if (Format == "Image"):
                self.data={
                    "status":self.status,
                    "event":self.event,
                    "temperature":self.temperature,
                    "humidity":self.humidity,
                    "flame":self.flame,
                    "thermal:":self.thermal,
                    "flame":self.flame,
                    "image":File_name
                }
        
            elif(Format == "video"):
                self.data ={
                    "status":self.detect_status,
                    "event":self.detect_event,
                    "temperature":self.temperature,
                    "humidity":self.humidity,
                    "flame":self.flame,
                    "thermal:":self.thermal,
                    "video":File_name, # ts_name
                    "m3u8":m3u8_name,   # m3u8_name
                    "image":jpg_name
                }
            result = requests.post(url,json = self.data,timeout=self.TIME_OUT)
            if(result.status_code == self.OK_CONNECT):
                print("Post success send to img or video")
            else:
                print("Post can't send signal because of some problem. error code : 400")
        except requests.exceptions.Timeout:
            print("Post request timeout. Failed to send img or video.")
            return  
        
        except requests.exceptions.RequestException as e:
            print(f"Failed to send img or video due to an exception: {e}")
            return
    
    def sendSignal(self):
        try:
            self.data = {}
            now = datetime.datetime.now(timezone.utc)
            str_now = str(now)
            #strTime = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:23] + 'Z'
            url = "http://"+self.HOST_NAME+"/api/sensor_data"
            self.data={
                "status":self.status,
                "event":self.event,
                "temperature":self.temperature,
                "flame":self.flame
            }
            result = requests.post(url,json = self.data,timeout=self.TIME_OUT)
            #print(result.text)
            if(result.status_code==self.OK_CONNECT):
                print("Post success to send server")
            else:
                print("Post can't send signal because of some problem. error code : 400")
        
        except requests.exceptions.Timeout:
            print("Post request timeout. Failed to send signal.")
            return  
        
        except requests.exceptions.RequestException as e:
            print(f"Failed to send signal due to an exception: {e}")
            
    def send_thermal_cam(self,event,cam_data):
        return
        try:
            self.data = {}
            now = datetime.datetime.now(timezone.utc)
            str_now = str(now)
            #strTime = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:23] + 'Z'
            url = "http://"+self.HOST_NAME+"/api/sensor_data"
            self.data = {
                "event": event,
                "msgTime":str_now,
                "signal":{
                    "d2":cam_data
                }
            }
            result = requests.post(url,json = self.data,timeout=self.TIME_OUT)
            #print(result.text)
            if(result.status_code==self.OK_CONNECT):
                print("Post success to send server")
            else:
                print("Post can't send signal because of some problem. error code : 400")
        
        except requests.exceptions.Timeout:
            print("Post request timeout. Failed to send signal.")
            return  
        
        except requests.exceptions.RequestException as e:
            print(f"Failed to send signal due to an exception: {e}")
 
    print("Post Loading complete")

    def POST_Write(Data):# data Write
        Connect.CreateFolder("POST")
        f = open("POST/POST.txt",'a')
        now=datetime.datetime.now()
        strTime = now.strftime('%Y_%m_%d_%H_%M_%S')
        strTemp = "[{strTime}]{Data}\r\n".format(strTime=strTime,Data=Data)
        f.write(strTemp)
        f.close()
        return strTemp
    
    def CreateFolder(strName):
        if not os.path.exists(strName):
            os.makedirs(strName)