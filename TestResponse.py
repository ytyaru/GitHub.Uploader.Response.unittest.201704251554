import unittest
from Response import Response
import requests
class TestResponse(unittest.TestCase):
    def test_Get_Json(self):
        url = 'https://api.github.com/users'
        kwargs = {'headers': {'Time-Zone': 'Asia/Tokyo', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': ''}}
        r = requests.get(url, **kwargs)
        # Content-Type: application/json;
        response = Response()
        res = response.Get(r)
        self.assertEqual('application/json', response.Headers.ContentType.mime_type)
        self.assertTrue(isinstance(res, list))
        self.assertEqual(type(res), list)
        self.assertTrue(0 < len(res))
        self.assertTrue(isinstance(res[0], dict))
        self.assertEqual(type(res[0]), dict)
    def test_Get_Text(self):
        url = 'https://www.google.co.jp/'
        kwargs = {'headers': {'User-Agent': ''}}
        r = requests.get(url, **kwargs)
        # Content-Type: text/html;
        response = Response()
        res = response.Get(r)
        self.assertEqual('text/html', response.Headers.ContentType.mime_type)
        self.assertTrue(isinstance(res, str))
        self.assertEqual(type(res), str)

    # Image, BeautifulSoupについてもテストすべきだが、今回はGitHubAPIが返すJSONさえ確認できればOKなので省略
