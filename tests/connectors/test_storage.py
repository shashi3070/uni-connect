import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


class TestLocalConnector(unittest.TestCase):
    def setUp(self):
        from uniconnect.connectors.storage.local import LocalConnector
        self.connector_cls = LocalConnector
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init(self):
        conn = self.connector_cls(config={"base_path": self.base_path})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["base_path"], self.base_path)

    def test_connect_sets_base_path(self):
        conn = self.connector_cls(config={"base_path": self.base_path})
        conn.connect()
        self.assertTrue(conn.is_connected)
        self.assertIsNotNone(conn.base_path)

    def test_write_read_delete(self):
        conn = self.connector_cls(config={"base_path": self.base_path})
        conn.connect()
        data = b"hello world"
        conn.write_file("test.txt", data)
        result = conn.read_file("test.txt")
        self.assertEqual(result, data)
        conn.delete_file("test.txt")
        self.assertFalse(conn.file_exists("test.txt"))

    def test_list_files(self):
        conn = self.connector_cls(config={"base_path": self.base_path})
        conn.connect()
        conn.write_file("a.txt", b"a")
        conn.write_file("b.txt", b"b")
        conn.write_file("sub" + os.sep + "c.txt", b"c")
        files = conn.list_files()
        self.assertIn("a.txt", files)
        self.assertIn("b.txt", files)
        self.assertIn("sub" + os.sep + "c.txt", files)
        conn.delete_file("a.txt")
        conn.delete_file("b.txt")
        conn.delete_file("sub" + os.sep + "c.txt")

    def test_list_files_with_prefix(self):
        conn = self.connector_cls(config={"base_path": self.base_path})
        conn.connect()
        conn.write_file("alpha.txt", b"x")
        conn.write_file("beta.txt", b"y")
        conn.write_file("sub" + os.sep + "gamma.txt", b"z")
        files_sub = conn.list_files(prefix="sub")
        self.assertIn("sub" + os.sep + "gamma.txt", files_sub)
        self.assertNotIn("alpha.txt", files_sub)
        conn.delete_file("alpha.txt")
        conn.delete_file("beta.txt")
        conn.delete_file("sub" + os.sep + "gamma.txt")

    def test_file_exists(self):
        conn = self.connector_cls(config={"base_path": self.base_path})
        conn.connect()
        self.assertFalse(conn.file_exists("nonexistent.txt"))
        conn.write_file("exists.txt", b"data")
        self.assertTrue(conn.file_exists("exists.txt"))
        conn.delete_file("exists.txt")

    def test_context_manager(self):
        with self.connector_cls(config={"base_path": self.base_path}) as conn:
            self.assertTrue(conn.is_connected)
            conn.write_file("ctx.txt", b"ctx")
            self.assertTrue(conn.file_exists("ctx.txt"))
        self.assertFalse(conn.is_connected)

    def test_path_traversal_protection(self):
        conn = self.connector_cls(config={"base_path": self.base_path})
        conn.connect()
        with self.assertRaises(PermissionError):
            conn.read_file("../etc/passwd")

    def test_not_connected_raises(self):
        conn = self.connector_cls(config={"base_path": self.base_path})
        with self.assertRaises(Exception):
            conn.read_file("test.txt")

    def test_list_files_empty_dir(self):
        conn = self.connector_cls(config={"base_path": self.base_path})
        conn.connect()
        empty_sub = os.path.join(self.base_path, "empty")
        os.makedirs(empty_sub, exist_ok=True)
        files = conn.list_files(prefix="empty")
        self.assertEqual(files, [])


class TestS3Connector(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.storage.s3 as mod
        importlib.reload(mod)
        self.connector_cls = mod.S3Connector

    def test_init(self):
        conn = self.connector_cls(config={"bucket": "test-bucket", "region": "us-east-1"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["bucket"], "test-bucket")

    def test_connect_no_driver(self):
        conn = self.connector_cls(config={"bucket": "test", "region": "us-east-1"})
        with self.assertRaises(ImportError):
            conn.connect()

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("storage", "s3")
        self.assertIs(cls, self.connector_cls)
        cls_boto3 = registry.get("storage", "s3", driver="boto3")
        self.assertIs(cls_boto3, self.connector_cls)
        cls_s3fs = registry.get("storage", "s3", driver="s3fs")
        self.assertIs(cls_s3fs, self.connector_cls)


class TestFTPConnector(unittest.TestCase):
    def setUp(self):
        from uniconnect.connectors.storage.ftp import FTPConnector
        self.connector_cls = FTPConnector

    def test_init(self):
        conn = self.connector_cls(config={"host": "localhost"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["host"], "localhost")


class TestSFTPConnector(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.storage.sftp as mod
        importlib.reload(mod)
        self.connector_cls = mod.SFTPConnector

    def test_init(self):
        conn = self.connector_cls(config={"host": "sftp.example.com", "user": "admin"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["host"], "sftp.example.com")

    def test_registration_with_drivers(self):
        from uniconnect.core.registry import registry
        cls = registry.get("storage", "sftp")
        self.assertIs(cls, self.connector_cls)
        cls_paramiko = registry.get("storage", "sftp", driver="paramiko")
        self.assertIs(cls_paramiko, self.connector_cls)
        cls_pysftp = registry.get("storage", "sftp", driver="pysftp")
        self.assertIs(cls_pysftp, self.connector_cls)


class TestGCSConnector(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.storage.gcs as mod
        importlib.reload(mod)
        self.connector_cls = mod.GCSConnector

    def test_init(self):
        conn = self.connector_cls(config={"bucket": "my-bucket", "project": "my-project"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["bucket"], "my-bucket")

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("storage", "gcs")
        self.assertIs(cls, self.connector_cls)
        cls_driver = registry.get("storage", "gcs", driver="google-cloud-storage")
        self.assertIs(cls_driver, self.connector_cls)


class TestAzureBlobConnector(unittest.TestCase):
    def setUp(self):
        from uniconnect.connectors.storage.azure_blob import AzureBlobConnector
        self.connector_cls = AzureBlobConnector

    def test_init(self):
        conn = self.connector_cls(config={
            "connection_string": "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=key==",
            "container_name": "mycontainer",
        })
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["container_name"], "mycontainer")


class TestStorageRegistration(unittest.TestCase):
    def test_all_storage_registered(self):
        from uniconnect import registry
        storage = registry.list_connectors().get("storage", [])
        expected = {"local", "s3", "ftp", "sftp", "gcs", "azure_blob"}
        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, storage, f"{name} not in storage connectors")


if __name__ == "__main__":
    unittest.main()
