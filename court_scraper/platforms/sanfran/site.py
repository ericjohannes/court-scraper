# court_scraper/platforms/sanfran/site.py

import json
import requests
from typing import List
from urllib.parse import urlparse
from urllib.parse import parse_qs
from selenium.webdriver.common.by import By
from court_scraper.case_info import CaseInfo
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from court_scraper.base.selenium_site import SeleniumSite
from court_scraper.utils import get_captcha_service_api_key
from selenium.webdriver.support import expected_conditions as EC

# note:
# what a expired session response looks like `{"result":[-1,""]}`

class Site(SeleniumSite):

    def __init__(self, place_id, manualcaptcha=False):
        self.place_id = place_id
        self.url = "https://webapps.sftc.org/ci/CaseInfo.dll"
        self.download_dir = self.get_download_dir()
        self.sessionid = self.__get_sessionid(headless=~manualcaptcha)

    def __get_sessionid(self, headless=True):
        self.driver = self._init_chrome_driver(headless=False)
        url = self.driver.get(self.url)
        # wait until captcha is broken and search form loads
        delay = 3 # seconds
        try:
            myElem = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.ID, 'NumberSearch')))
            parsed_url = urlparse(url)
            return parse_qs(parsed_url.query)['SessionID'][0]
        except TimeoutException:
            print("Loading took too much time!")
            return None
       

    def search(self, case_numbers=[], manualcaptcha=False) -> List[CaseInfo]:
        case_numbers = ['CUD97142814']
        endpoints = [
            {
                'name': 'register of actions',
                'endpoint': 'GetROA',
            },
            {
                'name': 'parties',
                'endpont': 'GetParties',
            },
            {
                'name': 'attorneys',
                'endpont': 'GetAttorneys',
            },
            {
                'name': 'calendar',
                'endpont': 'GetCalendar',
            },
            {
                'name': 'payments',
                'endpont': 'GetPayments',
            },
        ]
        for cn in case_numbers:
            case_data = {
                'main': None,
                'register of actions': None,
                'parties': None,
                'attorneys': None,
                'calendar': None,
                'payments': None,
            }
            params = {
                'CaseNum': cn,
                'SessionID': self.sessionid

            }
            # get main page
            r = requests.get(self.url, params=params)
            # todo: see what happens if you have an expired session when you do this
            # todo: see what html that you get back is like and figure out how to parse it
            for i in len(endpoints):
                ep = endpoints[i]
                ep_url = f'https://webapps.sftc.org/ci/CaseInfo.dll/datasnap/rest/TServerMethods1/GetROA/{ep['endpont']}/{self.sessionid}/' 
                r = requests.get(ep_url)
                data = r.json()
                new_data = json.loads(data['result'][1])
                if new_data is "": # session id expired, get a new one and try again
                    self.sessionid = self.__get_sessionid(headless=~manualcaptcha)
                    continue
                else:
                    case_data[ep['name']] = new_data
                    i += 1 # move onto next endpoint


        # Perform a place-specific search (using self.place_id)
        # for one or more case numbers.
        # Return a list of CaseInfo instances containing case metadata and,
        # if available, HTML for case detail page
        pass

    def search_by_date(self, filing_date=None) -> List[CaseInfo]:
        # Perform a place-specific, date-based search.
        # Defaut to current day if start_date and end_date not supplied.
        # Only scrape case metadata from search results pages by default.
        # If case_details set to True, scrape detailed case info
        # Apply case type filter if supported by site.
        # Return a list of CaseInfo instances
        pass

    def search_by_name(self, name) -> List[CaseInfo]:
        # search by a name
        url = f"https://webapps.sftc.org/ci/CaseInfo.dll/datasnap/rest/TServerMethods1/FindCaseName/{name}/{self.sessionid}/"
        r = requests.get(url)
        data = r.json()
        cases = json.loads(data['result'][1])
        # this is some junk that's not useful though
        return cases

