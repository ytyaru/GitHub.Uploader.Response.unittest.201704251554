import unittest
from Paginator import Paginator
from Response import Response
import requests
class TestPaginator(unittest.TestCase):
    def test_Paginate(self):
        response = Response()
        paginator = Paginator(response)
        
        # GitHubの全ユーザを取得する
        url = 'https://api.github.com/users'
        limit = 2 # 2ページ分までしか取得しない
        kwargs = {'headers': {'Time-Zone': 'Asia/Tokyo', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': ''}}
        res = paginator.Paginate(url, limit=limit)
        self.assertTrue(1 < len(res))
        self.assertEqual((30*limit), len(res)) # 1ページ30件(per_page=30)がデフォルト値のはず https://developer.github.com/v3/#pagination
        
