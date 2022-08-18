import unittest
from unittest import TestCase
import FinalV1
# from unittest.mock import Mock
# from unittest.mock import patch
class TestSum(TestCase):
    validXMLnotRSS = 'http://www-db.deis.unibo.it/courses/TW/DOCS/w3schools/xml/note.xml'
    validRSS = 'http://feeds.rssboard.org/rssboard'
    invalidDomain = 'http://invalid.local/'
    validRSSdata = FinalV1.httpGetFeed(validRSS)
    validXMLnotRSSdata = FinalV1.httpGetFeed(validXMLnotRSS)
    invalidDomaindata = FinalV1.httpGetFeed(invalidDomain)

    def setUp(self) -> None:
        print('\nRunning', self._testMethodName)
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()

    def test_httpGetFeed(self):
        ''' this checks httpGetFeed function on variety of good and bad data'''
        self.assertEqual(self.invalidDomaindata, False)
        self.assertGreater(len(self.validRSSdata), 120)
        self.assertGreater(len(self.validXMLnotRSSdata), 120)

    def test_checkIfRss(self):
        ''' this checks checkIfRss function '''
        self.assertEqual(FinalV1.checkIfRss(self.validRSSdata), True)
        self.assertEqual(FinalV1.checkIfRss(self.validXMLnotRSS), False)
        self.assertEqual(FinalV1.checkIfRss(self.invalidDomain), False)

    def test_parseRSS(self):
        ''' this checks function parseRSS on limited set of data because it gets filtered by checkIfRss and httpGetFeed functions
        also check if item limit works'''
        self.assertGreater(len(str(FinalV1.parseRSS(self.validRSSdata))), 18000)
        self.assertGreater(len(str(FinalV1.parseRSS(self.validRSSdata, 1))), 1800)

    def test_jsonPresentation(self):
        ''' test jsonPresentation function to see if json is returning'''
        nonjsonobject = {'test':0}
        self.assertEqual(FinalV1.jsonPresentation(nonjsonobject), '{"test": 0}')


    def test_userPresentation(self):
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
        self.assertEqual(len(FinalV1.userPresentation(object)), 3)
        self.assertEqual(len(FinalV1.userPresentation(objectTwo)), 4)
        pass

if __name__ == "__main__":
    unittest.main()