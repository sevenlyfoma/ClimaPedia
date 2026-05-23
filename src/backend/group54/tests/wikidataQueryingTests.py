import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/src")
from wikidataQuerying import infoQNo, SPARQLquery
from unittest.mock import patch
import requests


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
        
    if args[0] == "https://www.wikidata.org/w/api.php":
        return MockResponse({"result": "test data for infoQNo"}, 200)
    elif args[0] == "https://query.wikidata.org/sparql":
        return MockResponse({"result": "test data for SPARQLquery"}, 200)

    return MockResponse(None, 404)

class Tests(unittest.TestCase):

    @patch('wikidataQuerying.requests.get', side_effect=mocked_requests_get)
    def test_infoQNo(self, mock_get):
        """Test infoQNo function"""
        result = infoQNo('Q42')
        self.assertIn('result', result)
        self.assertEqual(result['result'], 'test data for infoQNo')

    @patch('wikidataQuerying.requests.get', side_effect=mocked_requests_get)
    def test_SPARQLquery(self, mock_get):
        """Test SPARQLquery function"""
        result = SPARQLquery("SELECT ?item WHERE { ?item wdt:P31 wd:Q5 .} LIMIT 1")
        self.assertIn('result', result)
        self.assertEqual(result['result'], 'test data for SPARQLquery')

if __name__ == '__main__':
    unittest.main()
