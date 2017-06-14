import unittest
from Response import Response
import requests
class TestLink(unittest.TestCase):
    def test_Singleton(self):
        # https://developer.github.com/guides/traversing-with-pagination/
        url_start = 'https://api.github.com/search/code?q=addClass+user:mozilla'
        r = requests.get(url_start)
        url_next = 'https://api.github.com/search/code?q=addClass+user%3Amozilla&page=2'
        link = Response.Headers.Link()
        
        self.assertEqual(url_start, r.url)
        self.assertEqual(url_next, link.Get(r))
        self.assertEqual(2, link.Next(r))
        self.assertTrue(2 < link.Last(r))
        
        """
        res = requests.Response()
        res.headers = {}
        url_next = 'https://api.github.com/search/code?q=addClass+user%3Amozilla&page=2'
        res.headers['Link'] = '<{url_next}>; rel="next", <https://api.github.com/search/code?q=addClass+user%3Amozilla&page=34>; rel="last"'.format(url_next=url_next)
        link = Response.Headers.Link()
        self.assertEqual(url_next, link.Get(res))
        """
