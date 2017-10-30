from unittest import TestCase
import pyostack


class IdentityTests(TestCase):
    def setUp(self):
        conf = pyostack.init("config.ini")
        self.identity = pyostack.Identity(conf)

    def test_list_tenants(self):
        tenants = self.identity.list_tenants()
        self.assertNotEqual(len(tenants), 0)
