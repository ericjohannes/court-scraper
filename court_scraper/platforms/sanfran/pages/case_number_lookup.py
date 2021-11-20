from bs4 import BeautifulSoup
from .case_detail import CaseDetailPage
from court_scraper.case_info import CaseInfo

class CaseNumberLookup:

    def __init__(self, place_id, session_id):
        self.place_id = place_id
        self.session_id = session_id

    def search(self, case_numbers=[]):
        results = []
        for cn in case_numbers:
            page = CaseDetailPage(self.place_id, cn)
            data = {'place_id': self.place_id}
            data.update(page.data)

            # params = {
            #     'CaseNum': cn,
            #     'SessionID': self.session_id

            # }
            # get main page
            # r = requests.get(self.url, params=params)
            # todo: see what happens if you have an expired session when you do this
            
            results.update(case_data)
            case = CaseInfo(data)
            results.append(case)
        