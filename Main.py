from tqdm import tqdm
from FileName import jsonName
from Crop import preImgProcess

js = jsonName()
crop = preImgProcess()
global CROPIMAGEMODE

def main():
    global CROPIMAGEMODE
    CROPIMAGEMODE = True
    if(CROPIMAGEMODE):
        js.filename()
        with tqdm(total=js.file_queue.qsize()) as pbar:
            while(True):
                if not(js.file_queue.empty()):
                    jsName = js.file_queue.get(block=False)
                    crop.LoadJson(jsName)
                    crop.image_process()
                    pbar.update(1)
                    continue
                break
    print("program is exit")

if __name__=="__main__":#main 실행하기
    main()
