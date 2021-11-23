from bs4 import BeautifulSoup
from .case_detail import CaseDetailPage
from .endpoint_detail import EndpointDetailPage
from court_scraper.case_info import CaseInfo

class CaseNumberLookup:

    def __init__(self, place_id, session_id):
        self.place_id = place_id
        self.session_id = session_id

    def search(self, case_numbers=[], details=False):
        results = []
        for cn in case_numbers:
            page = CaseDetailPage(self.place_id, cn, self.session_id)
            data = {'place_id': self.place_id}
            data.update(page.data)
            if details:
                for ep in self.endpoints:
                    ep_page = EndpointDetailPage(cn, ep, self.session_id)
                    data.update(ep_page.data)
            case = CaseInfo(data)
            # todo: check if this is rgith? this takes an like "data" and adds a key 'data' that is the value of the original 'data', ie data.data now == original data, and other key values of data are still there too
            results.append(case)
        return results
    
    @property
    def endpoints(self):
        return [
            {
                'name': 'register_of_actions',
                'endpoint': 'GetROA',
            },
            {
                'name': 'parties',
                'endpoint': 'GetParties',
            },
            {
                'name': 'attorneys',
                'endpoint': 'GetAttorneys',
            },
            {
                'name': 'calendar',
                'endpoint': 'GetCalendar',
            },
            {
                'name': 'payments',
                'endpoint': 'GetPayments',
            },
        ]