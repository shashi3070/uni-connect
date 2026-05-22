import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from uniconnect import connect, registry, BaseConnector
from uniconnect.core.base import SyncConnector, AsyncConnector
from uniconnect.core.exceptions import (
    ConfigurationError, ConnectionError, AuthenticationError,
    NotSupportedError, DriverNotFoundError, HealthCheckError,
)
from uniconnect.core.config import Config, detect_type, merge_configs, parse_connection_string, load_env_config
from uniconnect.core.utils import CredentialManager, retry, ConnectionPool
from uniconnect.core.factory import ConnectionFactory


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self._backup = registry._connectors.copy()
        registry._connectors.clear()

    def tearDown(self):
        registry._connectors.clear()
        registry._connectors.update(self._backup)

    def make_mock_connector(self, name="mock"):
        cls = MagicMock(spec=SyncConnector)
        cls.name = name
        return cls

    def test_registry_register_and_get(self):
        cls = self.make_mock_connector("test_con")
        registry.register("test_cat", "test_con", cls)
        result = registry.get("test_cat", "test_con")
        self.assertIs(result, cls)

    def test_registry_get_driver(self):
        cls = self.make_mock_connector("test_con")
        registry.register("test_cat", "test_con", cls, driver="v1")
        result = registry.get("test_cat", "test_con", driver="v1")
        self.assertIs(result, cls)

    def test_registry_get_not_found(self):
        with self.assertRaises(NotSupportedError):
            registry.get("nonexistent", "foo")

    def test_registry_get_driver_not_found(self):
        cls = self.make_mock_connector("test_con")
        registry.register("test_cat", "test_con", cls)
        with self.assertRaises(DriverNotFoundError):
            registry.get("test_cat", "test_con", driver="missing")

    def test_registry_list_connectors(self):
        cls = self.make_mock_connector("c1")
        registry.register("cat1", "c1", cls)
        registry.register("cat1", "c2", cls)
        registry.register("cat2", "c3", cls)
        result = registry.list_connectors()
        self.assertIn("cat1", result)
        self.assertIn("cat2", result)
        self.assertEqual(len(result["cat1"]), 2)
        self.assertEqual(len(result["cat2"]), 1)


class TestConfig(unittest.TestCase):
    def test_detect_type_from_uri(self):
        cases = [
            ("postgresql://host/db", ("databases", "postgres")),
            ("postgres://host/db", ("databases", "postgres")),
            ("s3://bucket/key", ("storage", "s3")),
            ("mysql://host/db", ("databases", "mysql")),
            ("mongodb://host/db", ("databases", "mongodb")),
            ("redis://host", ("databases", "redis")),
            ("ftp://host", ("storage", "ftp")),
            ("sftp://host", ("storage", "sftp")),
            ("file:///tmp", ("storage", "local")),
            ("sqlite:///:memory:", ("databases", "sqlite")),
            ("gs://bucket", ("storage", "gcs")),
            ("redshift://host/db", ("warehouse", "redshift")),
            ("snowflake://account", ("warehouse", "snowflake")),
            ("bigquery://project", ("warehouse", "bigquery")),
            ("kafka://host", ("streaming", "kafka")),
            ("mssql://host/db", ("databases", "sqlserver")),
            ("oracle://host/db", ("databases", "oracle")),
        ]
        for uri, expected in cases:
            with self.subTest(uri=uri):
                result = detect_type({"uri": uri})
                self.assertEqual(result, expected)

    def test_detect_type_unknown_uri(self):
        self.assertIsNone(detect_type({"uri": "unknown://foo"}))

    def test_detect_type_no_uri(self):
        self.assertIsNone(detect_type({}))

    def test_parse_connection_string(self):
        result = parse_connection_string("postgresql://user:pass@host:5432/db")
        self.assertEqual(result["type"], "postgresql")
        self.assertEqual(result["uri"], "postgresql://user:pass@host:5432/db")

    def test_parse_connection_string_no_scheme(self):
        result = parse_connection_string("justastring")
        self.assertEqual(result["type"], "unknown")

    def test_merge_configs(self):
        a = {"x": 1, "y": 2}
        b = {"y": 3, "z": 4}
        result = merge_configs(a, b)
        self.assertEqual(result, {"x": 1, "y": 3, "z": 4})

    def test_config_from_dict(self):
        cfg = Config.from_dict({"key": "val"})
        self.assertEqual(cfg.get("key"), "val")
        self.assertIsNone(cfg.get("missing"))
        self.assertEqual(cfg.get("missing", "default"), "default")

    def test_config_to_dict(self):
        cfg = Config.from_dict({"a": 1})
        self.assertEqual(cfg.to_dict(), {"a": 1})

    def test_config_merge(self):
        a = Config.from_dict({"x": 1})
        b = Config.from_dict({"y": 2})
        merged = a.merge(b)
        self.assertEqual(merged.get("x"), 1)
        self.assertEqual(merged.get("y"), 2)

    def test_load_env_config(self):
        with patch.dict(os.environ, {"UNICONNECT_TEST_KEY": "test_val"}, clear=True):
            cfg = load_env_config()
            self.assertIn("test_key", cfg)
            self.assertEqual(cfg["test_key"], "test_val")


class TestCredentialManager(unittest.TestCase):
    def test_from_config(self):
        mgr = CredentialManager({"api_key": "from_config"})
        self.assertEqual(mgr.get("api_key"), "from_config")

    def test_env_fallback(self):
        mgr = CredentialManager({})
        with patch.dict(os.environ, {"UNICONNECT_API_KEY": "from_env"}, clear=True):
            self.assertEqual(mgr.get("api_key"), "from_env")

    def test_env_direct_fallback(self):
        mgr = CredentialManager({})
        with patch.dict(os.environ, {"API_KEY": "direct_env"}, clear=True):
            self.assertEqual(mgr.get("api_key"), "direct_env")

    def test_default(self):
        mgr = CredentialManager({})
        self.assertEqual(mgr.get("missing", "default"), "default")

    def test_resolve(self):
        mgr = CredentialManager({"db_user": "admin"})
        result = mgr.resolve({"user": "db_user", "host": "HOST"})
        self.assertEqual(result["user"], "admin")
        self.assertIsNone(result["host"])


class TestRetry(unittest.TestCase):
    def test_retry_success_first(self):
        mock_fn = MagicMock(return_value="ok")
        decorated = retry(max_attempts=3)(mock_fn)
        result = decorated()
        self.assertEqual(result, "ok")
        mock_fn.assert_called_once()

    def test_retry_fails_then_succeeds(self):
        mock_fn = MagicMock(side_effect=[ValueError("fail"), ValueError("fail"), "ok"])
        decorated = retry(max_attempts=3, delay=0.01)(mock_fn)
        result = decorated()
        self.assertEqual(result, "ok")
        self.assertEqual(mock_fn.call_count, 3)

    def test_retry_exhausted(self):
        mock_fn = MagicMock(side_effect=ValueError("always fails"))
        decorated = retry(max_attempts=2, delay=0.01)(mock_fn)
        with self.assertRaises(ValueError):
            decorated()
        self.assertEqual(mock_fn.call_count, 2)


class TestConnectionPool(unittest.TestCase):
    def setUp(self):
        self._backup = registry._connectors.copy()
        registry._connectors.clear()

    def tearDown(self):
        registry._connectors.clear()
        registry._connectors.update(self._backup)

    def test_acquire_and_release(self):
        mock_cls = MagicMock(spec=SyncConnector)
        mock_inst = MagicMock(spec=SyncConnector)
        mock_inst.is_connected = True
        mock_cls.return_value = mock_inst

        pool = ConnectionPool(mock_cls, max_size=2, foo="bar")
        conn = pool.acquire()
        self.assertIs(conn, mock_inst)
        mock_cls.assert_called_once_with(config={"foo": "bar"})
        mock_inst.connect.assert_called_once()

        pool.release(conn)
        self.assertEqual(len(pool._pool), 1)

    def test_pool_exhausted(self):
        mock_cls = MagicMock(spec=SyncConnector)
        mock_inst = MagicMock(spec=SyncConnector)
        mock_inst.is_connected = True
        mock_cls.return_value = mock_inst

        pool = ConnectionPool(mock_cls, max_size=1)
        pool.acquire()
        with self.assertRaises(RuntimeError):
            pool.acquire()

    def test_close_all(self):
        mock_cls = MagicMock(spec=SyncConnector)
        mock_inst = MagicMock(spec=SyncConnector)
        mock_inst.is_connected = True
        mock_cls.return_value = mock_inst

        pool = ConnectionPool(mock_cls, max_size=2)
        conn = pool.acquire()
        pool.release(conn)
        pool.close_all()
        mock_inst.close.assert_called_once()
        self.assertEqual(len(pool._pool), 0)


class TestFactory(unittest.TestCase):
    def setUp(self):
        self._backup = registry._connectors.copy()
        registry._connectors.clear()
        self.mock_cls = MagicMock(spec=SyncConnector)
        self.mock_cls.return_value = MagicMock(spec=SyncConnector)
        registry.register("databases", "sqlite", self.mock_cls)
        registry.register("storage", "local", self.mock_cls)

    def tearDown(self):
        registry._connectors.clear()
        registry._connectors.update(self._backup)

    def test_connect_factory_uri_detection(self):
        connect("sqlite:///:memory:")
        self.mock_cls.assert_called()

    def test_connect_factory_type(self):
        connect("sqlite", {"path": ":memory:"})
        self.mock_cls.assert_called()

    def test_connect_factory_dict(self):
        connect({"type": "sqlite", "path": ":memory:"})
        self.mock_cls.assert_called()

    def test_connect_factory_invalid(self):
        with self.assertRaises(ConfigurationError):
            connect(123)

    def test_factory_kwargs(self):
        connect("sqlite", path=":memory:", driver=None)
        self.mock_cls.assert_called()


class TestBaseConnector(unittest.TestCase):
    def test_context_manager(self):
        calls = []
        class TestConn(BaseConnector):
            def connect(self):
                calls.append("connect")
                self._connected = True
            def close(self):
                calls.append("close")
                self._connected = False
        conn = TestConn()
        with conn:
            self.assertTrue(conn.is_connected)
        self.assertFalse(conn.is_connected)
        self.assertEqual(calls, ["connect", "close"])

    def test_is_connected_default(self):
        conn = MagicMock(spec=SyncConnector)
        conn.is_connected = False
        self.assertFalse(conn.is_connected)

    def test_health_check_default(self):
        conn = MagicMock(spec=SyncConnector)
        conn.health_check.return_value = True
        self.assertTrue(conn.health_check())


class TestSyncConnectorLifecycle(unittest.TestCase):
    def test_lifecycle(self):
        cls = MagicMock(spec=SyncConnector)
        inst = cls.return_value
        inst.is_connected = False
        inst.connect.side_effect = lambda: setattr(inst, 'is_connected', True)
        inst.close.side_effect = lambda: setattr(inst, 'is_connected', False)
        inst.connect()
        self.assertTrue(inst.is_connected)
        inst.close()
        self.assertFalse(inst.is_connected)


class TestExceptions(unittest.TestCase):
    def test_exception_hierarchy(self):
        self.assertTrue(issubclass(ConfigurationError, Exception))
        self.assertTrue(issubclass(ConnectionError, Exception))
        self.assertTrue(issubclass(AuthenticationError, ConnectionError))
        self.assertTrue(issubclass(NotSupportedError, Exception))
        self.assertTrue(issubclass(DriverNotFoundError, ConfigurationError))
        self.assertTrue(issubclass(HealthCheckError, ConnectionError))


if __name__ == "__main__":
    unittest.main()
