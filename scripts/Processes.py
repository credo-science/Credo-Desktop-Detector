import json
import multiprocessing
import time
import requests
import datetime
from scripts.DataTemplates import jsonTemplate

"""
To change to UTC
Change all time.time()*1000 -> datetime.datetime.utcnow().timestamp()*1000
"""

class Scheduler(multiprocessing.Process):
    """Send portion of data each sleep_time seconds. Require authentication token, queue with events and device info."""
    def __init__(self, sleep_time, tasks_to_be_done, device_id, device_type, device_model, system_version, app_version, send_request, auth_token):
        multiprocessing.Process.__init__(self)
        self.proc_name = self.name
        self.auth_token = auth_token
        self.send_request = send_request
        self.sleep_time = sleep_time
        self.tasks_to_be_done = tasks_to_be_done
        self.backup_queue = multiprocessing.JoinableQueue()
        self.device_id = device_id
        self.device_type = device_type
        self.device_model = device_model
        self.system_version = system_version
        self.app_version = app_version

    def killProcess(self):
        """Terminate process"""
        self.terminate()

    def backupData(self):
        data = []
        while self.backup_queue.qsize() != 0:
            data.append(self.backup_queue.get())
            self.backup_queue.task_done()
        for dat in data:
            try:
                result = self.send_request(dat, self.auth_token)
                print(f"Backup data stream status: {result}")
            except:
                self.backup_queue.put(dat)

    def run(self):
        data_template = jsonTemplate("Data")
        while True:
            try:
                time.sleep(self.sleep_time)
            except:
                self.terminate()
            _task_queue = []
            while self.tasks_to_be_done.qsize() != 0:
                _task_queue.append(self.tasks_to_be_done.get())
                self.tasks_to_be_done.task_done()
            try:
                data_content = data_template(_task_queue, self.device_id, self.device_type,
                                             self.device_model, self.system_version, self.app_version)  # whole data frame
                result = self.send_request(data_content, self.auth_token)
                print(f"Data stream status: {result}")
                if self.backup_queue.qsize() != 0:
                    self.backupData()
            except requests.exceptions.RequestException as e: 
                print (f"{e}, {self.sleep_time} seconds to retry.")
                self.backup_queue.put(data_content)
                # time.sleep(self.sleep_time)


class PingProcess(multiprocessing.Process):
    """Multiprocess for sending data"""

    def __init__(self, sleep_time, pings_to_be_done, ping_request, auth_token):
        multiprocessing.Process.__init__(self)
        self.pings_to_be_done = pings_to_be_done
        self.proc_name = self.name
        self.ping_request = ping_request
        self.auth_token = auth_token
        self.sleep_time = sleep_time

    def sendData(self):
        _ping_queue = []
        while self.pings_to_be_done.qsize() != 0:
            _ping_queue.append(self.pings_to_be_done.get())
            self.pings_to_be_done.task_done()
        for ping in _ping_queue:
            try:
                result = self.ping_request(ping, self.auth_token)
                print(f"Ping status: {result}")
            except requests.exceptions.RequestException as e: 
                print (f"{e}, {self.sleep_time} seconds to retry.")
                self.pings_to_be_done.put(ping)

    def run(self):
        while True:
            PingProcess.sendData(self)
            try:
                time.sleep(self.sleep_time)
            except:
                self.terminate()                
    def killProcess(self):
        """Terminate process"""
        PingProcess.sendData(self)
        self.terminate()
 
class PingScheduler(multiprocessing.Process):
    """Multiprocess with ping - ping information for how much time device is up"""

    def __init__(self, sleep_time, ping_tasks, ping_template, http_template,
                device_id, device_type, device_model, system_version, app_version):
        multiprocessing.Process.__init__(self)
        self.proc_name = self.name
        #self.start_time = int(time.time()*1000)
        self.start_time = int(datetime.datetime.utcnow().timestamp()*1000)
        self.sleep_time = sleep_time
        self.task_queue = ping_tasks
        self.ping_template = ping_template
        self.temp_time = 0
        self.current_time = 0
        self.device_id = device_id
        self.device_type = device_type
        self.device_model = device_model
        self.system_version = system_version
        self.app_version = app_version

    def run(self):
        while True:
            self.temp_time = int(datetime.datetime.utcnow().timestamp()*1000)
            try:
                time.sleep(self.sleep_time)
            except:
                self.terminate()
            self.current_time = int(datetime.datetime.utcnow().timestamp()*1000)
            # print(self.current_time - self.temp_time)
            pingFrame = self.ping_template(self.temp_time, 0, self.current_time - self.temp_time, self.device_id,
                                          self.device_type, self.device_model, self.system_version, self.app_version)
            self.task_queue.put(pingFrame)

    def killProcess(self):
        """Terminate process"""
        # pingFrame = self.ping_template(self.temp_time, 0, self.current_time - self.temp_time, self.device_id,
        #                                   self.device_type, self.device_model, self.system_version, self.app_version)
        # self.task_queue.put(pingFrame)
        # time.sleep(3)
        # FORCE PING REQUEST HERE!
        self.terminate()
