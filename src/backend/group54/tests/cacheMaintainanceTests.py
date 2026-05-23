import os
import sys
import auxiliaryFunctions

# sys.path.append(os.path.dirname(
# os.path.dirname(os.path.realpath(__file__))) + "/src")
# print(os.path.dirname(os.path.realpath(__file__)) + "/src")

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import cacheMaintainance as c

# TODO testing


class Tests(unittest.TestCase):

    def test__toStructurePerson(self):
        json_dict = {
            'person': {'value': 'https://www.wikidata.org/wiki/Q6194033'},
            'personLabel': {'value': 'Jim Cantore'},
            'borndate': {'value': '1964-02-16'},
            'coordPerson': {'value': '(52.161666666 21.048055555)'},
            'locLabel': {'value': 'Berlin'},
            'occLabel': {'value': 'meteorologist'},
            'deathDate': {'value': '2022-05-05'},
            'imageLabel': {'value': 'https://website.com/image.jpg'},
            'sexLabel': {'value': 'Male'}
            }

        expected_result = (
            6194033,
            'Jim Cantore',
            '1964-02-16',
            52.161666666,
            21.048055555,
            'Berlin',
            'meteorologist',
            '2022-05-05',
            'https://website.com/image.jpg',
            'Male'
            )

        self.assertEqual(c.toStructurePerson(json_dict), expected_result)
        self.assertEqual(c.toStructurePerson(json_dict), expected_result)

    def test__toStructureInstitution(self):

        line = {
            'educationOrEmployment':{'value':'https://www.wikidata.org/wiki/Q6194033'},
            'educationOrEmploymentLabel': {'value': "University of St Andrews"},
            'coordUni': {'value':"(52.161666666 21.048055555)"}
            }

        expected = (6194033,"University of St Andrews",52.161666666,21.048055555)
        result = c.toStructureInstitution(line)
        self.assertEqual(result, expected)

    def test__toStructureAttending(self):
        obj1 = {
            'person':{'value':'Q216273'},
            'educationOrEmployment':{'value':'Q6194033'},
            'educatePred':{'value':'P69'}
            }

        expected_result = (6194033, 216273, True)
        self.assertEqual(c.toStructureAttending(obj1),expected_result)

    def test__toStructureReceived(self):
        json_dict = {
            'person': {'value': 'https://www.wikidata.org/wiki/Q6194033'},
            'award':{'value':'https://www.wikidata.org/wiki/Q22058866'}
            }

        expected_result = (
            22058866,
            6194033
            )

        self.assertEqual(c.toStructureReceived(json_dict),expected_result)
        self.assertEqual(c.toStructureReceived(json_dict),expected_result)

    def test__toStructureAward(self):
        json_dict = {
            'award':{'value':'https://www.wikidata.org/wiki/Q22058866'},
            'awardLabel':{'value':"Grand Cross of the Order of the Dannebrog"}
            }

        expected_result = (
        22058866,
        "Grand Cross of the Order of the Dannebrog"
        )

        self.assertEqual(c.toStructureAward(json_dict),expected_result)
        self.assertEqual(c.toStructureAward(json_dict),expected_result)

    def test__toStructureMembership(self):
        json_dict = {
        'person':{'value':'https://www.wikidata.org/wiki/Q6194033'},
        'group':{'value':'https://www.wikidata.org/wiki/Q188771'}
        }

        expected_result = (
        188771,
        6194033
        )
        
        self.assertEqual(c.toStructureMembership(json_dict),expected_result)

    def test__toStructureGroup(self):
        obj1 = {'group':{'value':'Q12345'},'groupLabel':{'value':'some rats'}}
        retVal = (12345,'some rats')
        self.assertEqual(c.toStructureGroup(obj1),retVal)
        obj1 = {'group':{'value':'Q12345'},'groupLabel':{'value':'some rats'}}
        retVal = (12345,'some rats')
        self.assertEqual(c.toStructureGroup(obj1),retVal)


    def toStructureSatellite(self):
        obj1 = {
        'satellite':{'value':"https://www.wikidata.org/wiki/Q22058866"},
        'satelliteLabel':{'value':'Spacey'},
        'coords':{'value':'52.161666666,21.048055555'},
        'imageLabel':{'value':"https://website.com/image.jpg"}
        }

        expected_result = (22058866,'Spacey',52.161666666,21.048055555,"https://website.com/image.jpg")
        self.assertEqual(c.toStructureSatellite(obj1),expected_result)

    def toStructureSatelliteEvent(self):
        obj1 = {'satellite':{'value':"https://www.wikidata.org/wiki/Q22058866"},
        'eventLabel':{'value':'Massive Explosion!'},
        'eventTime':{'value':'1969-12-05T00:00:00Z'},
        'isEnd':{'value':'true'}
        }
        expected_result = (22058866,'Massive Explosion!','1969-12-05T00:00:00Z','true')
        self.assertEqual(c.toStructureSatelliteEvent(obj1),expected_result)

    if __name__ == '__main__':
        unittest.main()