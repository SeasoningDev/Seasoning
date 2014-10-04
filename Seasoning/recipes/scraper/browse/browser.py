from io import BytesIO
from urllib2 import build_opener, HTTPError, URLError, Request,\
    HTTPCookieProcessor
from bs4 import BeautifulSoup
import urllib, time, gzip
from recipes.scraper.browse.redirecter import Redirecter
from cookielib import LWPCookieJar
import json

class Browser(object):
    """
    This is the browser used by the API to browse around on autogids.be.
    
    To seem humanlike, the browser has the following features:
        * Random waiting time between requests
        * Automatic pathfinding between last-visited page, and the given url to browse to
        * Mozilla Firefox Headers
        * Referer Header is filled in automatically according to last visited page
    
    """
    class IncompleteResponseException(Exception):
        def __init__(self, url):
            Exception.__init__(self)
            self.url = url
    
    HEADER =  {'Host' : None,
               'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
               'Accept' : '*/*',
               'Accept-Language' : 'en-us;q=0.7,en;q=0.3',
               'Accept-Encoding' : 'gzip, deflate',
               'Accept-Charset' : 'utf-8;q=0.7,*;q=0.7',
               'Connection': 'keep-alive',}   
    COOKIES_FILE = 'cookies.lwp' 
    
    retries = 0
    last_visited_url = None
    
    def __init__(self, host):
        self.host = host
        self.HEADER['Host'] = host
        
        self.cj = LWPCookieJar()
        
#         if os.path.isfile(self.COOKIES_FILE):
#             self.cj.load(self.COOKIES_FILE)
            
        cookieHandler = HTTPCookieProcessor(self.cj)
        redirectHandler = Redirecter()
         
        self.opener = build_opener(redirectHandler, cookieHandler)

    def _get(self, url, post_dict=None, referer=None, delay_ms=0):
        '''
        This is an internal method used by the get and post methods
        '''
        # Construct the post data if it is available
        data = None
        if post_dict:
            data = urllib.urlencode(post_dict)
            data = data.encode('utf_8')
        
        # Construct the request header
        header = Browser.HEADER
#         if referer is None and self.last_visited_url is not None:
#             # Default value: use previously visited page
#             header['Referer'] = self.last_visited_url
#         elif referer:
#             # Given value: is this value
#             if 'http://www.autogids.be/' not in referer:
#                 referer = 'http://www.autogids.be/' + referer
#             header['Referer'] = referer
            
        # Make the request
        while True:
            try:
                url = url.encode('utf-8')
                req = Request(url, data, header)            
                handle = self.opener.open(req)
                last_visited_url = handle.geturl()
                self.retries = 0
                break
            except (HTTPError, URLError) as e:
                if self.retries < 3:
                    time.sleep(1)
                    self.retries += 1
                    continue
                raise e
        
        # Get the request html; decode if necessary
        response = ''
        while 1:
            data = handle.readline()
            if not data or data == "":
                break
            response += data
        data = response
        self.raw_data = data
        
        if handle.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(data)
            f = gzip.GzipFile(fileobj=buf)
            page = f.read()
        else:
            page = data
        
        if 'application/json' in handle.info().get('Content-Type'):
            page = json.loads(page)
        else:
            page = BeautifulSoup(page)
        
        # Put the request url in the browsing history
        self.last_visited_url = last_visited_url
        
        if '<html>' in self.raw_data and not '</html>' in self.raw_data:
            raise self.IncompleteResponseException(last_visited_url)
        
        return page

    def get(self, url, delay=0, force_refresh=False):
        return self._get(url, delay_ms=delay)
    
    def post(self, url, post_dict, delay=0):
        """
        Posts the given data to the given url.
        The browser will not automatically browse to the given page before posting, so 
        make sure this has been taken care of if you want to look human.
        
        """
        return self._get(url, post_dict, delay_ms=delay)
