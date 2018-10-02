"""Data Templates"""
def makeDataFrame(accuracy, altitude, latitude, longitude, provider ,timestamp ,pulse ,temperature, humidity, pressure):
    """Generate JSON data frame of detector event"""
    frame = {
        "accuracy": accuracy,
        "altitude": altitude,
        "latitude": latitude,
        "longitude": longitude,
        "provider": provider,
        "timestamp": timestamp,
        "pulse_height": pulse,
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure
    }
    return frame

def jsonTemplate(which_template):
    """Get one of parameter: Register, Login, SendData and return template as a function"""
    def register(email, username, display_name, password, team, language, device_id, device_type, device_model, system_version, app_version):
        """Return Register JSON template"""
        template_ = {
            "email": email,
            "username": username,
            "display_name": display_name,
            "password": password,
            "team": team,
            "language": language,
            "device_id": device_id,
            "device_type": device_type,
            "device_model": device_model,
            "system_version": system_version,
            "app_version": app_version
        }
        return template_

    def login(username, password, device_id, device_type, device_model, system_version, app_version):
        """Return Login JSON template"""
        template_ = {
            "username": username,
            "password": password,
            "device_id": device_id,
            "device_type": device_type,
            "device_model": device_model,
            "system_version": system_version,
            "app_version": app_version
        }
        return template_

    def sendData(data_jlist, device_id, device_type, device_model, system_version, app_version):
        """Return Data JSON template"""
        template_ = {
        "detections": 
                data_jlist,
            "device_id": device_id,
            "device_type": device_type,
            "device_model": device_model,
            "system_version": system_version,
            "app_version": app_version
        }
        return template_

    def ping(timestamp, delta_time, on_time, device_id, device_type, device_model, system_version, app_version):
        """Return Ping JSON template"""
        template_ = {
            "timestamp": timestamp,
            "delta_time": delta_time,
            "on_time": on_time,
            "device_id": device_id,
            "device_type": device_type,
            "device_model": device_model,
            "system_version": system_version,
            "app_version": app_version
        }
        return template_

    if which_template == "Register":
        return register
    elif which_template == "Login":
        return login
    elif which_template == "Data":
        return sendData
    elif which_template == "Ping":
        return ping
