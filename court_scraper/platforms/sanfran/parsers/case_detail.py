from bs4 import BeautifulSoup

class CaseDetailParser:

    def __init__(self, html):
        self.html = html
    
    def parse(self):
        fe_list = self._font_element_list
        payload = {
            'case_title': self._case_title(self._font_element_list),
            'cause_of_action': self._cause_of_action(self._font_element_list),
        }
        return payload

    @property
    def _font_element_list(self):
        try:
            return self._fe_list
        except AttributeError:
            soup = BeautifulSoup(self.html, 'html.parser')

            font_elems = list(soup.find_all('font'))
            '''
            these font elements have a pattern like
            "Case Number:\n"
            <case number>
            'Title:\n'
            <case title>
            'Cause of Action:\n'
            <cause of action>
            <junk>
            <junk>
            etc.

            so this methods works off the expectation that indexofkey + 1 == indexofvalue
            '''
            font_elems = soup.find_all('font')
            text_of_fonts = []
            for fe in font_elems:
                text_of_fonts.append(fe.text)
            self._fe_list = text_of_fonts
            return text_of_fonts
    
    def _case_title(self, fe_list):
        # if the key isn't in the html then it will skip getting the value too
        try:
            title_i = fe_list.index('Title:\n') + 1
            return fe_list[title_i]
        except:
            return None # maybe there was no title in the data?
    
    def _cause_of_action(self, fe_list):
        # the key isn't in the html then it will skip getting the value too
        try: 
            cause_i = fe_list.index('Cause of Action:\n') + 1
            return fe_list[cause_i]
        except:
            return None # not there
