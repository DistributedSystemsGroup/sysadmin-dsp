from unittest import TestCase
import pyostack


class MeteringTests(TestCase):
    def setUp(self):
        conf = pyostack.init("config.ini")
        self.metering = pyostack.Metering(conf)

    def test_meter_list(self):
        meters = self.metering.meter_list()
        self.assertNotEqual(len(meters), 0)
