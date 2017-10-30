from unittest import TestCase
import pyostack


class ComputeTests(TestCase):
    def setUp(self):
        conf = pyostack.init("config.ini")
        self.compute = pyostack.Compute(conf)

    def test_server_list(self):
        servers = self.compute.server_list()
        self.assertNotEqual(len(servers), 0)
