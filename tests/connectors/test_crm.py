import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


class TestSalesforceConnector(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.crm.salesforce as mod
        importlib.reload(mod)
        self.connector_cls = mod.SalesforceConnector

    def test_init(self):
        conn = self.connector_cls(config={
            "username": "admin@example.com",
            "password": "pass",
            "security_token": "token",
        })
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["username"], "admin@example.com")

    def test_registration_with_drivers(self):
        from uniconnect.core.registry import registry
        cls = registry.get("crm", "salesforce")
        self.assertIs(cls, self.connector_cls)
        cls_ss = registry.get("crm", "salesforce", driver="simple_salesforce")
        self.assertIs(cls_ss, self.connector_cls)
        cls_pysfdc = registry.get("crm", "salesforce", driver="pysfdc")
        self.assertIs(cls_pysfdc, self.connector_cls)

    def test_connect_missing_driver(self):
        conn = self.connector_cls(config={
            "username": "admin@example.com",
            "password": "pass",
        })
        with patch.dict('sys.modules', {'simple_salesforce': None}):
            import importlib
            import uniconnect.connectors.crm.salesforce as mod
            importlib.reload(mod)
            conn2 = mod.SalesforceConnector(config={
                "username": "admin@example.com",
                "password": "pass",
            })
            with self.assertRaises(ImportError):
                conn2.connect()


class TestHubSpotConnector(unittest.TestCase):
    def setUp(self):
        from uniconnect.connectors.crm.hubspot import HubSpotConnector
        self.connector_cls = HubSpotConnector

    def test_init(self):
        conn = self.connector_cls(config={"access_token": "pat-test"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["access_token"], "pat-test")


class TestCRMRegistration(unittest.TestCase):
    def test_all_crm_registered(self):
        from uniconnect import registry
        crm = registry.list_connectors().get("crm", [])
        expected = {
            "salesforce", "hubspot", "zoho", "pipedrive",
            "zendesk", "freshdesk", "intercom", "marketo",
            "ms_dynamics", "netsuite", "sap_crm", "servicenow",
            "sugarcrm",
        }
        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, crm, f"{name} not in crm connectors")


if __name__ == "__main__":
    unittest.main()
