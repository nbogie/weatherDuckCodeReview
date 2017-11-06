import weatherPi
import unittest
class TestWeatherPi(unittest.TestCase):

    def test_LEDColourForWeatherID(self):
        f = weatherPi.LEDColourForWeatherID
        self.assertEqual(1, f(199))
        self.assertEqual(2, f(200))
        self.assertEqual(2, f(299))
        self.assertEqual(1, f(300))
        self.assertEqual(1, f(399))
        self.assertEqual(1, f(500))
        self.assertEqual(1, f(599))
        self.assertEqual(1, f(600))
        self.assertEqual(1, f(699))
        self.assertEqual(2, f(700))
        self.assertEqual(2, f(799))
        self.assertEqual(0, f(800))
        self.assertEqual(0, f(899))
        self.assertEqual(2, f(900))
        self.assertEqual(2, f(906))
        self.assertEqual(1, f(907))
        self.assertEqual(1, f(950))
        self.assertEqual(0, f(951))
        self.assertEqual(0, f(956))
        self.assertEqual(0, f(957))
        self.assertEqual(0, f(962))
        self.assertEqual(1, f(963))

        self.assertEqual(1, f(0))
        self.assertEqual(1, f(400))
        self.assertEqual(1, f(499))


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
