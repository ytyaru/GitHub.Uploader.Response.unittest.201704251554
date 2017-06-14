import unittest
from Response import Response
import logging
class TestHeaders(unittest.TestCase):
    def test_HasContentType(self):
        h = Response.Headers()
        self.assertTrue(hasattr(h, 'ContentType'))
