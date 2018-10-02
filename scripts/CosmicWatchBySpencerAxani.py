# Code made by https://github.com/spenceraxani

import serial 
import time
import glob
import sys
import json
from datetime import datetime
from multiprocessing import Process
import random
import logging

def serialPorts():
        """ Lists serial port names
            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

class CosmicWatch():
    def killProcess(self):
        self.ComPort.close()     

    def __init__(self):
        port_list = serialPorts()
        if len(port_list) > 1:
            print('Available serial ports:\n')
            for i in range(len(port_list)):
                print('['+str(i+1)+'] ' + str(port_list[i]))
            print('[h] help\n')
            ArduinoPort = input("Select Arduino Port:")
            if ArduinoPort == 'h':
                print('\n===================== help =======================')
                print('1. Is your Arduino connected to the serial USB port?\n')
                print('2. Check that you have the correct drivers installed:\n')
                print('\tMacOS: CH340 driver')
                print('\tWindows: no dirver needed')
                print('\tLinux: no driver needed')
                sys.exit()
        else :
            ArduinoPort = 1
        print("The selected port is:")
        try:
            print(str(port_list[int(ArduinoPort)-1])+'\n')
        except:
            print("No device connected!")
            sys.exit() 

        #ComPort = serial.Serial('/dev/cu.wchusbserialfa130') # open the COM Port
        self.ComPort = serial.Serial(port_list[int(ArduinoPort)-1]) # open the COM Port
        self.ComPort.baudrate = 9600          # set Baud rate
        self.ComPort.bytesize = 8             # Number of data bits = 8
        self.ComPort.parity   = 'N'           # No parity
        self.ComPort.stopbits = 1    

        logging.basicConfig(level=logging.WARNING)
        print(self.ComPort)

    def gatherTheData(self):
        data = self.ComPort.readline()
        return data
