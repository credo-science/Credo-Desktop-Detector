### This is the prototype of Credo Desktop Detektor Aplication.

You can run Cosmic Watch and gather data to dedicated API by runing python3.6 RunCosmic.py or by running a binary.

for more info run:
```
python3.6 RunCosmic.py -h or RunCosmic -h
```
For running code in python interpreter you need to install:
	python 3.6+
	python3-serial

If you can't read data form serial port you may have to change permissions or run CREDO Watch as a super user. 

Another option is to execute following line: 
```
sudo chmod 666 /dev/ttyUSB0
```

We suggest to create a binary file using **pyinstaller**. 
