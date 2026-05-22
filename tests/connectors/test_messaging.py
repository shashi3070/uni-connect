import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


class TestSMTPConnector(unittest.TestCase):
    def setUp(self):
        from uniconnect.connectors.messaging.email_smtp import SMTPConnector
        self.connector_cls = SMTPConnector

    def test_init(self):
        conn = self.connector_cls(config={
            "host": "smtp.example.com",
            "user": "test@example.com",
            "password": "pass",
        })
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["host"], "smtp.example.com")

    def test_send_no_connection(self):
        conn = self.connector_cls(config={"host": "smtp.example.com"})
        with self.assertRaises(Exception):
            conn.send(to="user@example.com", subject="Test", body="Hello")


class TestSendGridConnector(unittest.TestCase):
    def setUp(self):
        from uniconnect.connectors.messaging.sendgrid import SendGridConnector
        self.connector_cls = SendGridConnector

    def test_init(self):
        conn = self.connector_cls(config={"api_key": "SG.test"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["api_key"], "SG.test")


class TestSlackConnector(unittest.TestCase):
    def setUp(self):
        from uniconnect.connectors.messaging.slack import SlackConnector
        self.connector_cls = SlackConnector

    def test_init(self):
        conn = self.connector_cls(config={"token": "xoxb-test"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["token"], "xoxb-test")


class TestTwilioConnector(unittest.TestCase):
    def setUp(self):
        from uniconnect.connectors.messaging.twilio import TwilioConnector
        self.connector_cls = TwilioConnector

    def test_init(self):
        conn = self.connector_cls(config={
            "account_sid": "AC-test",
            "auth_token": "tok-test",
            "from_number": "+15551234567",
        })
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["account_sid"], "AC-test")

    def test_connect_missing_creds(self):
        conn = self.connector_cls(config={})
        with self.assertRaises(ValueError):
            conn.connect()

    def test_connect_missing_driver(self):
        conn = self.connector_cls(config={
            "account_sid": "AC-test",
            "auth_token": "tok-test",
        })
        with patch.dict('sys.modules', {'twilio.rest': None}):
            import importlib
            import uniconnect.connectors.messaging.twilio as mod
            importlib.reload(mod)
            conn2 = mod.TwilioConnector(config={
                "account_sid": "AC-test",
                "auth_token": "tok-test",
            })
            with self.assertRaises(ImportError):
                conn2.connect()


class TestMessagingRegistration(unittest.TestCase):
    def test_all_messaging_registered(self):
        from uniconnect import registry
        msg = registry.list_connectors().get("messaging", [])
        expected = {
            "email_smtp", "email_imap", "sendgrid", "mailgun",
            "mailchimp", "slack", "teams", "discord", "telegram",
            "twilio", "pushbullet", "onesignal", "fcm",
        }
        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, msg, f"{name} not in messaging connectors")


if __name__ == "__main__":
    unittest.main()
