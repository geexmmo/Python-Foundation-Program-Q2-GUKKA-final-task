import logging
import unittest
from unittest import TestCase
import FinalV1
# from unittest.mock import Mock
# from unittest.mock import patch

class TestSum(TestCase):
    validXMLnotRSS = 'http://www-db.deis.unibo.it/courses/TW/DOCS/w3schools/xml/note.xml'
    validRSS = 'http://feeds.rssboard.org/rssboard'
    invalidDomain = 'http://invalid.local/'
    validRSSdata = FinalV1.http_get_feed(validRSS)
    validXMLnotRSSdata = FinalV1.http_get_feed(validXMLnotRSS)
    invalidDomaindata = FinalV1.http_get_feed(invalidDomain)
    filename = ''

    def setUp(self) -> None:
        print('\nRunning', self._testMethodName)
        return super().setUp()


    def tearDown(self) -> None:
        return super().tearDown()


    def test_http_get_feed(self):
        ''' this checks httpGetFeed function on variety of good and bad data'''
        self.assertEqual(self.invalidDomaindata, False)
        self.assertGreater(len(self.validRSSdata), 120)
        self.assertGreater(len(self.validXMLnotRSSdata), 120)


    def test_check_if_rss(self):
        ''' this checks checkIfRss function '''
        self.assertEqual(FinalV1.check_if_rss(self.validRSSdata), True)
        self.assertEqual(FinalV1.check_if_rss(self.validXMLnotRSS), False)
        self.assertEqual(FinalV1.check_if_rss(self.invalidDomain), False)


    def test_parse_rss(self):
        ''' this checks function parseRSS on limited set of data because it gets filtered by checkIfRss and httpGetFeed functions
        also check if item limit works'''
        self.assertGreater(len(str(FinalV1.parse_rss(self.validRSSdata))), 18000)
        self.assertGreater(len(str(FinalV1.parse_rss(self.validRSSdata, 1))), 1800)


    def test_json_presentation(self):
        ''' test jsonPresentation function to see if json is returning'''
        nonjsonobject = {'test':0}
        self.assertEqual(FinalV1.json_presentation(nonjsonobject), '{"test": 0}')


    def test_user_presentation(self):
        ''' test function userPresentation, checks object with 1 items and object with 2 items'''
        object = {"0 ": {
                    "title": "channel title",
                    "description": "channel description",
                    "language": "en-us",
                    "link": "https://channel-url",
                    "items": [
                    {
                        "title": "item title",
                        "link": "https://item-url",
                        "description": "item text",
                        "pubDate": "Wed, 02 Apr 2014 11:12:53 -0400 - item publication date"
                    }]}}
        objectTwo = {"0 ": {
                    "title": "channel title",
                    "description": "channel description",
                    "language": "en-us",
                    "link": "https://channel-url",
                    "items": [
                    {
                        "title": "item title",
                        "link": "https://item-url",
                        "description": "item text",
                        "pubDate": "Wed, 02 Apr 2014 11:12:53 -0400 - item publication date"
                    },
                    {
                        "title": "item title2",
                        "link": "https://item-url2",
                        "description": "item text2",
                        "pubDate": "Wed, 02 Apr 2014 11:12:53 -0400 - item publication date"
                    }]}}
        # print(len(''.join(FinalV1.user_presentation(object, False))))
        self.assertEqual(len(''.join(FinalV1.user_presentation(object, False))), 253)
        self.assertEqual(len(FinalV1.user_presentation(objectTwo, False)), 11)


    def test_make_filename(self):
        filename = FinalV1.make_filename('http://www.local/rssfeed', '/tmp/cache/')
        self.assertEqual(filename, '/tmp/cache/httpwwwlocalrssfeed')


    def test_cache_make(self):
        filename = FinalV1.make_filename('http://www.local/rssfeed', '/tmp/')
        FinalV1.cache_make({'test':[{'a':'b'},{'c':'d'}]},filename)
        try:
            with open(filename, 'r'):
                opened = True
        except FileNotFoundError as err:
            print(f'Failed {err}')
        self.assertAlmostEqual(opened, True)


    def test_cache_check_path(self):
        filename = FinalV1.make_filename('http://www.local/rssfeed', '/tmp/')
        FinalV1.cache_make({'test':[{'a':'b'},{'c':'d'}]},filename)
        self.assertEqual(FinalV1.cache_check_path(filename),True)


    def test_validate_date(self):
        self.testt = 'HARD'
        self.assertEqual(FinalV1.validate_date('2022/02/01'), 1643652000)
        self.assertEqual(FinalV1.validate_date('202/02/01'), False)
        self.assertEqual(FinalV1.validate_date('2022/02/41'), False)


    def test_cache_find_by_date(self):
        filename = '/tmp/httpwwwlocalrssfeed'
        testobject = {"0 ": {
            "title": "channel title",
            "description": "channel description",
            "language": "en-us",
            "link": "https://channel-url",
            "items": [
            {
                "title": "item title",
                "link": "https://item-url",
                "description": "item text",
                "pubDate": "Wed, 02 Apr 2014 11:12:53 -0400"
            }]}}
        FinalV1.cache_make(testobject, filename)
        test1 = FinalV1.cache_find_by_date(filename, FinalV1.validate_date('2014/04/02'))
        test2 = FinalV1.cache_find_by_date(filename, FinalV1.validate_date('2000/01/01'))
        self.assertGreater(len(repr(test1)), 50)
        self.assertEqual(test2, False)

if __name__ == "__main__":
    unittest.main()
