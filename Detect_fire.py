import cv2
from yolov5.detect import Detect
from multiprocessing import Process,Queue,Lock
import time
class Detection:
    def __init__(self):
        self.D = Detect()
        self.D.model_path='/home/szbaijie/F_RCMS/fire_model.pt'
        self.opt = self.D.parse_opt()
        self.D.check_req()
    
    def run(self,c,q):
    # 화재 검출 실행
        try:
            print("Detect")
            self.D.main(self.opt,c,q)
        except:
            print("Detection err")
            time.sleep(1)
            self.D.main(self.opt,c,q)
print("Detection loading complete")
# # # 비디오 캡처 객체 생성
class cam:

    def cam_read(self,c,q):
         # 프레임 읽기
         try:
             while True:
                 _, frame = c.read()
                 cv2.imshow("NORMAL_IMG",frame)
                 cv2.waitKey(1)
                 q.put(frame)
                 if(q.qsize()>=5):
                     q.get()
                     continue
         except KeyboardInterrupt:
             self.cap.release()
             print("keyboard interrupt is occur")


# c = cam()
# d = Detection()
# q = Queue()
# cap = cv2.VideoCapture(0)
# def main():
    
    
#     c_p = Process(target= c.cam_read,args=([cap,q]))
#     d_p = Process(target = d.run,args=([cap,q]))
#     c_p.start()
#     d_p.start()
#     c_p.join()
#     d_p.join()
    

# if __name__ == "__main__":
#     main()