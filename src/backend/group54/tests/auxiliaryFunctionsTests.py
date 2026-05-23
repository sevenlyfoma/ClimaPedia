import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(__file__)) + "/src")
import auxiliaryFunctions

# TODO testing


class Tests(unittest.TestCase):

    def test_extractQNumberFromURL(self):
        url = "https://www.wikidata.org/wiki/Q9120329"
        self.assertEqual(auxiliaryFunctions.extractQNumberFromURL(url), 9120329)
        # pass

    def test_extractCoordsCase1(self):
        # Test case 1
        pointStr = "Warsaw University of Life Sciences(52.161666666 21.048055555)"
        self.assertEqual(
            auxiliaryFunctions.extractCoords(pointStr), (52.161666666, 21.048055555)
        )

    def test_extractCoordsCase2(self):
        # Test case 2
        pointStr2 = 'University of Ljubljana(46.048888888 14.503888888)'
        self.assertEqual(auxiliaryFunctions.extractCoords(pointStr2),(46.048888888,14.503888888))

if __name__ == '__main__':
    unittest.main()
