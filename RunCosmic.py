#!/usr/bin/env python3.6
"""
@todo Catch server not respond
@todo Catch bad port
@todo prevent from to small interval
@bug no ping and start
@todo replace sleeps to timers
@todo time to UTC
"""
import json
import getpass
import os
import platform
import time
import hashlib
import random
import multiprocessing
import signal
import argparse

# INSECURE
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Local libs
from scripts.CosmicWatchBySpencerAxani import CosmicWatch, sys
from scripts.DataTemplates import makeDataFrame, jsonTemplate
from scripts.RequestTemplates import httpRequest
from scripts.Processes import Scheduler, PingProcess, PingScheduler, datetime

class Klasa():
    # APPLICATION SETUP
    def __init__(self):
        """Variables"""
        self.altitude = 210.73
        self.longitude = 50.0922
        self.latitude = 19.9148
        parser = argparse.ArgumentParser()
        parser.add_argument("-l","--latitude", help="latitude", type=float)
        parser.add_argument("-o","--longitude", help="longitude", type=float)
        parser.add_argument("-a","--altitude", help="altitude", type=float)

        parser.add_argument("-i","--interval", help="interval in seconds between each pack of JSON data", type=int, default=600)
        parser.add_argument("-s","--server", help="adress of CREDO API", type=str, default="https://api.credo.science")
        parser.add_argument("-g","--gui", help="turns on GUI", action="store_true", default=False)
        parser.add_argument("-p","--port", help="select port", type=str, default="600")
        args = parser.parse_args()

        """Actions for variables"""
        self.altitude = args.altitude
        self.longitude = args.longitude
        self.latitude = args.latitude


        self.GUI = args.gui
        #if args.gui == True:
        print(f"GUI: {args.gui}")

        #if args.port:
        self.PORT = args.port
        print(f"Selected port: {args.port}")
        #else:
        #    self.PORT = 600
        #    print(f"\tPort: {self.PORT}")

        #if args.interval:
        self.TIME_INTERVAL = args.interval
        print(f"Selected: {args.interval} interval")
        #else:
        #    self.TIME_INTERVAL = 600
        #    print(f"\tTime interval: {self.TIME_INTERVAL}")

        #if args.server:
        self.SERVER = args.server
        print(f"Selected: {args.server} server")
        #else:
        #    self.SERVER = "https://api.credo.science"
        #    print(f"\tDefault server: {self.SERVER}")

        #print("Args:")
        #print(args)

        # Constant App parameters
        self.config_file_name = '.CosmicConfig.json'
        self.distro, self.version, self.kernel = platform.linux_distribution()
        self.device_type = "Desktop"
        self.device_model = "CosmicWatch"
        self.system_version = platform.system() + platform.release() + " " + self.distro + self.version
        self.app_version = 0.2

        # variables for GUI version
        # self.authentication_token = None
        # self.device_id = None
        # self.Detector = None

        # Processes
        self.schedule_pings = None
        self.request_pings_process = None
        self.send_data_process = None

    """Functions"""
    def signalHandler(self, sig, frame):
        self.Detector.killProcess()
        # schedule_pings must end before request_pings_process 
        self.schedule_pings.killProcess() #send last ping to be done
        self.request_pings_process.killProcess() #send last pings and terminates
        self.send_data_process.killProcess()
        print('You pressed Ctrl+C!')
        sys.exit(0)

    def generateUniqueID(self, device_model, device_type, user_name):
        id_ = hashlib.md5(
            bytes(f"{device_model}{device_type}{user_name}", 'utf-8')).hexdigest()
        id_ = str(id_) + str(int(time.time()))
        return id_

    def errors(self, statusCode, content):
        """Chcecks for 400 and 500 status code from server.
                If status code == 400 or 500 return True
                Else returns False
        """
        if statusCode == 400 or statusCode == 500:
            print(
                f"There is {statusCode} status Code from server: \"{json.loads(content)['message']}\"")
            return True
        else:
            return False

    def ifConfigExist(self):
        """Check if configure file exists. If True returns data from file, if not returns False"""
        try:
            with open(self.config_file_name) as config_file:
                _data_ = json.load(config_file)
                return(_data_)
        except:
            return False

    def InitiateCosmicWatch(self):
        """Guide thruu registering process, returns JSON template for http request"""
        if self.GUI == False:
            print("No config file detected!")
            print("Register your detector:")
            print("email:")
            email = input()
            print("username:")
            user_name = input()
            print("displayName:")
            display_Name = input()

            password = getpass.getpass('password:')
            password_repeat = getpass.getpass('repeat your password:')
            if password != password_repeat:
                print("Passwords are not the same!")
                self.InitiateCosmicWatch()
                return 0
            print("team:")
            team = input()
            print("language:")
            language = input()

        template = jsonTemplate("Register")
        self.device_id = self.generateUniqueID(
            self.device_model, self.device_type, user_name)
        return template(email, user_name, display_Name, password, team, language, 
                        self.device_id, self.device_type, self.device_model, self.system_version, self.app_version)

    def Init(self):
        """Initialization of Detector"""
        config = self.ifConfigExist()
        if config == False:
            registration_template = self.InitiateCosmicWatch()
            register_request = httpRequest(self.SERVER, "Register")
            register_result = register_request(registration_template)
            config_file = open(self.config_file_name, 'w')
            self.device_id = registration_template['device_id']
            if self.errors(register_result[0], register_result[2]) == False:
                del registration_template['password']
                config_file.write(json.dumps(registration_template, indent=4))
                config_file.close
                config = self.ifConfigExist()
            elif json.loads(register_result[2])['message'] == "Registration failed. Reason: User with given username or email already exists.":
                del registration_template['password']
                config_file.write(json.dumps(registration_template, indent=4))
                config_file.close
                config = self.ifConfigExist()
                print('Config file recreated!')
        else:
            file_ = open(self.config_file_name).read()
            self.device_id = json.loads(file_)['device_id']
            # file_.close()

    # Loggin into server
    def LogIn(self, username, password):
        """Return Auth Token -- authentication_token"""
        template = jsonTemplate("Login")
        login_template = template(username, password, self.device_id, self.device_type,
                                 self.device_model, self.system_version, self.app_version)

        login_request = httpRequest(self.SERVER, "Login")
        login_result = login_request(login_template)
        if self.errors(login_result[0], login_result[2]) == False:
            pass
        else:
            sys.exit()
        return json.loads(login_result[2])['token']

    def StartStreaming(self):
        """Handle sreaming processes for pings and data stream process"""
        # Generate Templates Send Data and Ping
        send_request = httpRequest(self.SERVER, "Data")
        ping_request = httpRequest(self.SERVER, "Ping")

        # Multiprocessing Task Queues
        tasks = multiprocessing.JoinableQueue()
        ping_tasks = multiprocessing.JoinableQueue()

        # Initialize Cosmic Watch
        self.Detector = CosmicWatch()
        counter = 0
        print("Taking data ...")
        print("Press ctl+c to terminate process")
        signal.signal(signal.SIGINT, self.signalHandler)

        # Create data scheduler process 
        self.send_data_process = Scheduler(self.TIME_INTERVAL, tasks, self.device_id, self.device_type, self.device_model,
                                     self.system_version, self.app_version, send_request, self.authentication_token)

        # Create ping scheduler processes
        self.schedule_pings = PingScheduler(self.TIME_INTERVAL, ping_tasks, jsonTemplate("Ping"), ping_request, self.device_id,
                                            self.device_type, self.device_model, self.system_version, self.app_version)
        self.request_pings_process = PingProcess(self.TIME_INTERVAL, ping_tasks, ping_request, self.authentication_token)

        # Start Processes
        self.schedule_pings.start(), self.request_pings_process.start()
        self.send_data_process.start()

        # Schedule data to send
        while True:
            data = self.Detector.gatherTheData()    # Wait and read data
            if counter != 0:
                # print(f"recived particle no.: {counter}")
                amplitude = (str(data).split(" ")[3])
                dframe_template = makeDataFrame(1, self.altitude, self.latitude, self.longitude, "manual", int(datetime.datetime.utcnow().timestamp()*1000),
                 amplitude, None, None, None)  # data framme
                # print(str(datetime.datetime.utcnow().timestamp()*1000))
                tasks.put(dframe_template)
            counter += 1

    def MainWork(self):
        """Main work"""
        # print("Hello! I'm working very hard...")

        self.Init()
        if self.GUI == False:
            print("To start data streaming, please login:")
            print("username:")
            username = input()
            password = getpass.getpass('password:')
            self.authentication_token = self.LogIn(username, password)
        else:
            self.authentication_token = self.LogIn(None, None)
        self.StartStreaming()

    def TestTest(self):
        for x in range(100):
            print("TEST ", x)

if __name__ == '__main__':
    program = Klasa()
    program.MainWork()

