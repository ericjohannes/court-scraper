# court_scraper/platforms/sanfran/site.py

import json
import requests
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import parse_qs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from court_scraper.case_info import CaseInfo
from .pages.case_number_lookup import CaseNumberLookup
from court_scraper.base.selenium_site import SeleniumSite
from court_scraper.utils import get_captcha_service_api_key
# note:
# what a expired session response looks like `{"result":[-1,""]}`
# todo:
# add a method of site that makes requests and gets a new session id based on some results and updates session id of the site if it needs to
class Site(SeleniumSite):

    def __init__(self, place_id, manual_captcha=False):
        self.place_id = place_id
        self.url = "https://webapps.sftc.org/ci/CaseInfo.dll"
        self.retries = 5 # limit number of times it can try to get a session id
        self.download_dir = self.get_download_dir()
        self.manual_captcha = manual_captcha
        self.sessionid = self.__get_sessionid(headless=not self.manual_captcha)

    def __get_sessionid(self, headless=True):
        if self.retries < 0:
            print('tried to make a session too many times')
            exit()
        self.retries -= 1
        self.driver = self._init_chrome_driver(headless=False)
        url = self.driver.get(self.url)
        # wait until captcha is broken and search form loads
        delay = 60 # seconds to break captcha
        try:
            myElem = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.ID, 'NumberSearch'))) # execution waits until page loads
            parsed_url = urlparse(self.driver.current_url)
            sessionid = parse_qs(parsed_url.query)['SessionID'][0]
            self.driver.quit()
            return sessionid
        except TimeoutException:
            print("Loading took too much time!")
            return None
       

    def search(self, case_numbers=[], details=False) -> List[CaseInfo]:
        # Perform a place-specific search (using self.place_id)
        # for one or more case numbers.
        # Return a list of CaseInfo instances containing case metadata and,
        # if available, HTML for case detail page
        lookup = CaseNumberLookup(self.place_id, self.sessionid)       
        cases = lookup.search(case_numbers=case_numbers, details=details)

        return cases

    def search_by_date(self, filing_date=None, case_details=False, manual_captcha=False) -> List[CaseInfo]:
        # Perform a place-specific, date-based search.
        # Defaut to current day if start_date and end_date not supplied.
        # Only scrape case metadata from search results pages by default.
        # If case_details set to True, scrape detailed case info
        # Apply case type filter if supported by site.
        # Return a list of CaseInfo instances
        if filing_date is None:
            filing_date = datetime.today().strftime('%Y-%m-%d')
        
        endpoint = f"{self.url}/datasnap/rest/TServerMethods1/GetCasesWithFilings/{filing_date}/{self.sessionid}/"
        r = requests.get(endpoint)
        data = r.json()
        if data[0] is -1: # no session id or it's expired
            self.sessionid = self.__get_sessionid(headless=not manual_captcha)
            r = requests.get(endpoint) # try again
            data = r.json()
        elif data[0] is 0:
            return None # no records
        else: # there's data
            raw_cases = json.loads(data['result'][1])
            cases = []
            for c in raw_cases:
                soup = BeautifulSoup(c['CASE_NUMBER'], 'html.parser')
                case_number = soup.find('a').text
                case_info = CaseInfo({'number': case_number, 'place_id': self.place_id, 'case_title': c['CASE_TITLE'], 'filing_date': filing_date})
                cases.append(case_info)
        if case_details:
            # todo get more info on cases more elegantly
            cases = self.search([c.number for c in cases], manual_captcha=manual_captcha)
        return cases

    def search_by_name(self, name) -> List[CaseInfo]:
        # search by a name
        url = f"https://webapps.sftc.org/ci/CaseInfo.dll/datasnap/rest/TServerMethods1/FindCaseName/{name}/{self.sessionid}/"
        r = requests.get(url)
        data = r.json()
        cases = json.loads(data['result'][1])
        # this is some junk that's not useful though
        return cases

