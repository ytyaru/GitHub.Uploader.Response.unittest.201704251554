import unittest
from Response import Response
import requests
class TestResponse(unittest.TestCase):
    def test_GitHubApiDefault(self):
        top_level_type = 'application'
        sub_type = 'json'
        mime_type = '{top_level_type}/{sub_type}'.format(top_level_type=top_level_type, sub_type=sub_type)
        char_set = 'utf-8'
        res = requests.Response()
        res.headers = {}
        res.headers['Content-Type'] = '{mime_type}; charset={char_set}'.format(mime_type=mime_type, char_set=char_set)
        c = Response.Headers.ContentType()
        c.Split(res)
        self.assertEqual(mime_type, c.mime_type)
        self.assertEqual(top_level_type, c.top_level_type)
        self.assertEqual(sub_type, c.sub_type)
        self.assertEqual(char_set, c.char_set)
        self.assertTrue('charset' in c.parameters.keys())
        self.assertEqual(char_set, c.parameters['charset'])
        self.assertEqual(None, c.suffix)
        
    def test_MultiParameter(self):
        # https://ja.wikipedia.org/wiki/%E3%83%A1%E3%83%87%E3%82%A3%E3%82%A2%E3%82%BF%E3%82%A4%E3%83%97#.E5.91.BD.E5.90.8D.E8.A6.8F.E5.89.87
        top_level_type = 'text'
        sub_type = 'plain'
        mime_type = '{top_level_type}/{sub_type}'.format(top_level_type=top_level_type, sub_type=sub_type)
        char_set = 'iso-2022-jp'
        res = requests.Response()
        res.headers = {}
        res.headers['Content-Type'] = '{mime_type}; charset={char_set}; format=flowed; delsp=yes'.format(mime_type=mime_type, char_set=char_set)
        c = Response.Headers.ContentType()
        c.Split(res)
        self.assertEqual(mime_type, c.mime_type)
        self.assertEqual(top_level_type, c.top_level_type)
        self.assertEqual(sub_type, c.sub_type)
        self.assertEqual(char_set, c.char_set)
        self.assertTrue('charset' in c.parameters.keys())
        self.assertEqual(char_set, c.parameters['charset'])
        self.assertTrue('format' in c.parameters.keys())
        self.assertEqual('flowed', c.parameters['format'])
        self.assertTrue('delsp' in c.parameters.keys())
        self.assertEqual('yes', c.parameters['delsp'])
        self.assertEqual(None, c.suffix)

    # バグ発見。suffixが取得できていなかった。
    def test_Suffix(self):
        # https://developer.github.com/v3/media/
        top_level_type = 'application'
        suffix = 'json'
        # サブタイプ名はツリー、サブタイプ名、サフィックスに分けられるらしい。が、細かすぎるのでまとめてサブタイプ名とした。
        # https://ja.wikipedia.org/wiki/%E3%83%A1%E3%83%87%E3%82%A3%E3%82%A2%E3%82%BF%E3%82%A4%E3%83%97#.E5.91.BD.E5.90.8D.E8.A6.8F.E5.89.87
        sub_type = 'vnd.github.v3+{suffix}'.format(suffix=suffix)
        mime_type = '{top_level_type}/{sub_type}'.format(top_level_type=top_level_type, sub_type=sub_type)
        char_set = 'utf-8'
        res = requests.Response()
        res.headers = {}
        res.headers['Content-Type'] = '{mime_type}; charset={char_set}'.format(mime_type=mime_type, char_set=char_set)
        c = Response.Headers.ContentType()
        c.Split(res)
        self.assertEqual(mime_type, c.mime_type)
        self.assertEqual(top_level_type, c.top_level_type)
        self.assertEqual(sub_type, c.sub_type)
        self.assertEqual(char_set, c.char_set)
        self.assertTrue('charset' in c.parameters.keys())
        self.assertEqual(char_set, c.parameters['charset'])
        self.assertEqual(suffix, c.suffix)

        """
        l2 = Log()
        self.assertTrue(l1 is l2)
        self.assertTrue(l1 is Log())
    def test_Handler(self):
        self.assertTrue(Log().Logger.hasHandlers())
    def test_Logger(self):
        self.assertEqual(logging.DEBUG, Log().Logger.getEffectiveLevel())
        Log().Logger.setLevel(logging.INFO)
        self.assertEqual(logging.INFO, Log().Logger.getEffectiveLevel())
    """
