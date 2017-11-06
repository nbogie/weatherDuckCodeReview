import weatherPi
from weatherPi import Colour

import unittest

class TestWeatherPi(unittest.TestCase):

    def test_pinForLEDColour(self):
        f = weatherPi.pinForLEDColour
        self.assertEqual(13, f(Colour.YELLOW))
        self.assertEqual(19, f(Colour.BLUE))
        self.assertEqual(26, f(Colour.RED))
        self.assertEqual(19, f(None))


    def test_LEDColourForWeatherID(self):
        f = weatherPi.LEDColourForWeatherID
        self.assertEqual(Colour.BLUE, f(199))
        self.assertEqual(Colour.RED, f(200))
        self.assertEqual(Colour.RED, f(299))
        self.assertEqual(Colour.BLUE, f(300))
        self.assertEqual(Colour.BLUE, f(399))
        self.assertEqual(Colour.BLUE, f(500))
        self.assertEqual(Colour.BLUE, f(599))
        self.assertEqual(Colour.BLUE, f(600))
        self.assertEqual(Colour.BLUE, f(699))
        self.assertEqual(Colour.RED, f(700))
        self.assertEqual(Colour.RED, f(799))
        self.assertEqual(Colour.YELLOW, f(800))
        self.assertEqual(Colour.YELLOW, f(899))
        self.assertEqual(Colour.RED, f(900))
        self.assertEqual(Colour.RED, f(906))
        self.assertEqual(Colour.BLUE, f(907))
        self.assertEqual(Colour.BLUE, f(950))
        self.assertEqual(Colour.YELLOW, f(951))
        self.assertEqual(Colour.YELLOW, f(956))
        self.assertEqual(Colour.YELLOW, f(957))
        self.assertEqual(Colour.YELLOW, f(962))
        self.assertEqual(Colour.BLUE, f(963))

        self.assertEqual(Colour.BLUE, f(0))
        self.assertEqual(Colour.BLUE, f(400))
        self.assertEqual(Colour.BLUE, f(499))


    def test_motorDirectionForWindDirection(self):
        f = weatherPi.motorDirectionForWindDirection
        self.assertEqual(0, f(0))
        self.assertEqual(0, f(45))
        self.assertEqual(0, f(360))

        self.assertEqual(16.2, f(46))
        self.assertEqual(16.2, f(90))
        self.assertEqual(32.4, f(91))
        self.assertEqual(32.4, f(135))
        
        self.assertEqual(48.6, f(136))
        self.assertEqual(48.6, f(180))
        
        self.assertEqual(64.8, f(181))
        self.assertEqual(64.8, f(225))

        self.assertEqual(81, f(226))
        self.assertEqual(81, f(270))

        self.assertEqual(97.2, f(271))
        self.assertEqual(97.2, f(315))
        
        self.assertEqual(113.4, f(316))
        self.assertEqual(113.4, f(359))

        self.assertEqual(0, f(361))
        
if __name__ == '__main__':
    unittest.main()
