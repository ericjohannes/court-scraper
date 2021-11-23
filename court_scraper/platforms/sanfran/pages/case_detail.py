import requests

from ..parsers.case_detail import CaseDetailParser

class CaseDetailPage:

    def __init__(self, place_id, case_number, session_id, parser_kls=CaseDetailParser):
        self.url = "https://webapps.sftc.org/ci/CaseInfo.dll"
        self.place_id = place_id
        self.case_number = case_number
        self.session_id = session_id
        self.parser_kls = parser_kls

    
    @property
    def data(self):
        payload = {
            'number': self.case_number,
            'html': self.html,
        }
        parser = self.parser_kls(self.html)
        extra_data = parser.parse()
        payload.update(extra_data)
        return payload
    
    @property
    def html(self):
        try:
            return self._output
        except AttributeError:
            params = {
                'CaseNum': self.case_number,
                'SessionID': self.session_id
            }
            response = requests.get(self.url, params=params)
            _html = response.text
            self._output = _html
            return _html

    
    @property
    def details(self):
        for ep in self.endpoints:

