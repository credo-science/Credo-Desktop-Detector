"""Request"""
import requests

def httpRequest(IP, which_request):
    """choose IP adress of server and select type of request: Register, Login, SendData."""
    def registerRequest(dataJSON):
        """Http Register request to server"""
        _adress = str(IP) + "/api/v2/user/register"
        r = requests.post(_adress, json=dataJSON, verify=False, headers={'Content-Type': 'application/json'}, timeout=10)
        return(r.status_code, r.reason, r.content)
        
    def loginRequest(dataJSON):
        """Http Login request to server"""
        _adress = str(IP) + "/api/v2/user/login"
        r = requests.post(_adress, json=dataJSON, verify=False, headers={'Content-Type': 'application/json'}, timeout=10)
        return(r.status_code, r.reason, r.content)

    def sendDataRequest(dataJSON, token):
        """Http SendData request to serverl"""
        _adress = str(IP) + "/api/v2/detection"
        header = {'Content-Type': 'application/json', 'Authorization': 'Token {}'.format(token)}
        r = requests.post(_adress, json=dataJSON, verify=False, headers=header, timeout=10)
        return(r.status_code, r.reason, r.content)

    def ping(dataJSON, token):
        """Http Ping request to server"""
        _adress = str(IP) + "/api/v2/ping"
        header = {'Content-Type': 'application/json', 'Authorization': 'Token {}'.format(token)}
        r = requests.post(_adress, json=dataJSON, verify=False, headers=header, timeout=10)
        return(r.status_code, r.reason, r.content)

    if which_request == "Register":
        return registerRequest
    elif which_request == "Login":
        return loginRequest
    elif which_request == "Data":
        return sendDataRequest
    elif which_request == "Ping":
        return ping