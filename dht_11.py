import time
import Adafruit_Python_DHT.Adafruit_DHT as Adafruit_DHT
class dht_11:
    def __init__(self):
        self.sensor = Adafruit_DHT.DHT11
        self.pin = 4
    
    def q_dht(self):# return humidith, temp (100,100)
        try : 
            h, t = Adafruit_DHT.read_retry(self.sensor,self.pin)
            
            return h,t
        except : 
            return None,None


