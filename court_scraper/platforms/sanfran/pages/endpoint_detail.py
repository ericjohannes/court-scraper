import json
import requests

class EndpointDetailPage:

    def __init__(self, case_number, endpoint, session_id):
        self.url = f"https://webapps.sftc.org/ci/CaseInfo.dll/datasnap/rest/TServerMethods1/{endpoint['endpoint']}/{case_number}/{session_id}/"
        self.name = endpoint['name']
    
    @property
    def data(self):
        r = requests.get(self.url)
        data = r.json()
        if data[0] is -1: # permission denied, session id probably expired
            return {self.name: None }
        elif data[0] is 0: # are none of this type of record so returna  string that says so
            return {self.name: str(data['result'][1])}
        else: # there is data
            return {self.name: json.loads(data['result'][1])}