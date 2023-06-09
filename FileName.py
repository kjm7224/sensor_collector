import os
import queue

class jsonName():
    # 검색하고자 하는 폴더 경로
    def __init__(self):
        self.folder_path = "C:\kjm\Repository\Test_AI\labelingData"
        self.file_queue = queue.Queue()
    def filename(self):
        # 폴더 탐색
        for root, dirs, files in os.walk(self.folder_path):
            # 폴더 안에 있는 모든 파일 경로를 큐에 넣기
            for file in files:
                file_path = os.path.join(root, file)
                self.file_queue.put(file_path)
                
 