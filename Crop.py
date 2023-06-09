import json
import cv2
import os

class preImgProcess:
    def __init__(self):
        self.FolderName = "TeachImg"
        self.data = None
        self.image_path = ""
        self.image_name = ""
        self.img = None
        self.cropped_img=None
        self.absdir = os.getcwd()
        self.jsonFolderName = "C:\kjm\Repository\Test_AI\labelingData"
    
    def CreateFolder(self,FolderName):
        self.FolderName = FolderName
        if not os.path.exists(self.FolderName):
            os.makedirs(self.FolderName)
    
    def LoadJson(self,jsonName):
        # JSON 파일 로드
        with open(jsonName, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        return

    def image_process(self):
        # 이미지 경로 생성
        self.image_path = self.absdir +'\\'+ self.data['image']['path'] + '\\' + self.data['image']['filename']
        # 이미지 로드
        self.img = cv2.imread(self.image_path)
        
        #이미지 이름 저장
        self.image_name = self.data['image']['filename']
        # bounding box 좌표 추출
        box = self.data['annotations'][0]['box']
        x1, y1, x2, y2 = box

        # 이미지 crop
        self.cropped_img = self.img[y1:y2, x1:x2]
        self.show_img()
        
    def show_img(self):
        # 결과 이미지 저장
        self.CreateFolder("Teach_Image")
        self.image_path=self.absdir+'\\'+self.FolderName+'\\'+self.image_name
        cv2.imwrite(self.image_path, self.cropped_img)

