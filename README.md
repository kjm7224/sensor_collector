# PT-Sensor data collection and Fire extinguishing device control with Raspi

## preprocessing process

- [ ] [install openCV](https://velog.io/@kaiseong/%EB%9D%BC%EC%A6%88%EB%B2%A0%EB%A6%AC%ED%8C%8C%EC%9D%B4-OpenCV%EC%84%A4%EC%B9%98)
    This website shows you how to install opencv.
    해당 웹사이트를 참조하여 opencv를 설치한다.


## checking your Version 

- [ ] python version 3.9.2
- [ ] opencv version 4.7.0
- [ ] Rpi.GPIO 0.7.0
- [ ] ffmpeg 4.3.5-0
- [ ] postgresql 13
```
# query openCV version
$ python -c "import cv2; print(cv2.__version__)"

# query python version
$ python --version

# install Rpi.GPIO
$ pip3 install RPi.GPIO

# qeury Rpi.GPIO
$ pip3 show RPi.GPIO

# query ffmpeg version
$ ffmpeg -version

# install postgresql
$ sudo apt install postgresql

# query postgresql version
$ dpkg -l | grep postgresql

# how to install dht-11 library
1. $ git clone https://github.com/adafruit/Adafruit_Python_DHT.git 
2. $ cd Adafruit_Python_DHT
3. $ sudo python setup.py install

and then, you can see this log is written "Finished processing dependencies for Adafruit-DHT==1.4.0"

```

## Flow Chart

- [ ] [click here](https://drive.google.com/file/d/18G5ZhFl6PBVuhIz7MnyxPZpYv3I1N-qm/view?usp=sharing)


# how to run file
- [ ] write 'python-run' on terminal then, sensor collector script will start
```
python-run
```

## Copyright
nest I&C own F_RCMS Copyright 
if you want to know detail impormaion in this project, send email
email address is kjm7224@nestinc.co.kr

## Project status
this project started at 2023 in march
project is not yet complete and some bug exist
we'll improve that

## bug report
- 2023_04_12 
```
edge pulse signal is abnormal
Video time of ts file extension needs to be modified
Speed improvement

```
