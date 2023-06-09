import time
from tqdm import tqdm
class Char():
    def __init__(self):
        self.pbar = None
        self.total = 10
        self.upcnt=1
        self.cur_time = 0
        self.pre_Time = 0
        self.progressbar_flag = False
        self.cnt = 0
    def dog():
        dog = '''
                    / \__
                    (    @\___
                    /         O
                /   (_____/
                /_____/   U
            /|/|  /|_|_|\\
        /_|\|\/ /_/ \_\\
        '''
        print(dog)

    def progressbar_Start(self,set_time):
        self.pbar = tqdm(total=set_time,bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} , recordFlag convert to True]")
        self.progressbar_flag=True

    def progressbar(self,Time):
        self.pbar.update(Time)

    def show_progressbar(self,Time,set_time):
        Time = int(round(Time,0))
        self.cur_time = Time
        if Time < set_time:
            if not(self.cur_time==self.pre_Time):
                Char.progressbar(self,1)
                self.cnt+=1
        else:
            if(self.progressbar_flag):
                if not(self.cnt==set_time):
                    self.cnt+=1
                    Char.progressbar(self,1)
                    return
                self.cnt=0
                print("\r\n\r\n\r\nRecord flag will be ready for pause")
                self.progressbar_flag = False
                self.pbar.close()
                return
        self.pre_Time =  self.cur_time

    print("Charcter loading complete")