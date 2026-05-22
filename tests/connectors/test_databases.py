import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


class TestSQLiteConnector(unittest.TestCase):
    def setUp(self):
        from uniconnect.connectors.databases.sqlite import SQLiteConnector
        self.connector_cls = SQLiteConnector

    def test_init(self):
        conn = self.connector_cls(config={"path": ":memory:"})
        self.assertIsNotNone(conn)
        self.assertFalse(conn.is_connected)

    def test_create_table_and_insert(self):
        conn = self.connector_cls(config={"path": ":memory:"})
        conn.connect()
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO test (name) VALUES (?)", ("Alice",))
        conn.close()
        self.assertFalse(conn.is_connected)

    def test_query(self):
        conn = self.connector_cls(config={"path": ":memory:"})
        conn.connect()
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO test (name) VALUES (?)", ("Alice",))
        conn.execute("INSERT INTO test (name) VALUES (?)", ("Bob",))
        rows = conn.query("SELECT * FROM test ORDER BY id")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "Alice")
        self.assertEqual(rows[1]["name"], "Bob")
        conn.close()

    def test_execute_rowcount(self):
        conn = self.connector_cls(config={"path": ":memory:"})
        conn.connect()
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO test (name) VALUES ('X')")
        conn.execute("INSERT INTO test (name) VALUES ('Y')")
        count = conn.execute("UPDATE test SET name = 'Z' WHERE name = 'X'")
        self.assertIsNotNone(count)
        conn.close()

    def test_context_manager(self):
        with self.connector_cls(config={"path": ":memory:"}) as conn:
            self.assertTrue(conn.is_connected)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.execute("INSERT INTO test VALUES (1)")
            rows = conn.query("SELECT * FROM test")
            self.assertEqual(len(rows), 1)
        self.assertFalse(conn.is_connected)

    def test_not_connected_error(self):
        conn = self.connector_cls(config={"path": ":memory:"})
        with self.assertRaises(Exception):
            conn.query("SELECT 1")

    def test_auto_detect_from_uri(self):
        from uniconnect import connect
        conn = connect({"type": "sqlite", "path": ":memory:"})
        conn.connect()
        conn.execute("CREATE TABLE t (v INTEGER)")
        conn.execute("INSERT INTO t VALUES (42)")
        rows = conn.query("SELECT * FROM t")
        self.assertEqual(rows[0]["v"], 42)
        conn.close()


class TestDuckDBConnector(unittest.TestCase):
    def setUp(self):
        from uniconnect.connectors.databases.duckdb import DuckDBConnector
        self.connector_cls = DuckDBConnector

    def test_init(self):
        conn = self.connector_cls(config={"path": ":memory:"})
        self.assertIsNotNone(conn)
        self.assertFalse(conn.is_connected)

    def test_no_driver_installed(self):
        with patch.dict('sys.modules', {'duckdb': None}):
            import importlib
            import uniconnect.connectors.databases.duckdb as mod
            importlib.reload(mod)
            conn = mod.DuckDBConnector(config={"path": ":memory:"})
            with self.assertRaises(ImportError):
                conn.connect()


class TestPostgreSQLRegistration(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.databases.postgres as mod
        importlib.reload(mod)
        self.connector_cls = mod.PostgreSQLConnector

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("databases", "postgres")
        self.assertIs(cls, self.connector_cls)
        cls_psycopg2 = registry.get("databases", "postgres", driver="psycopg2")
        self.assertIs(cls_psycopg2, self.connector_cls)
        cls_asyncpg = registry.get("databases", "postgres", driver="asyncpg")
        self.assertIs(cls_asyncpg, self.connector_cls)


class TestMySQLRegistration(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.databases.mysql as mod
        importlib.reload(mod)
        self.connector_cls = mod.MySQLConnector

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("databases", "mysql")
        self.assertIs(cls, self.connector_cls)
        cls_1 = registry.get("databases", "mysql", driver="mysql-connector-python")
        self.assertIs(cls_1, self.connector_cls)
        cls_2 = registry.get("databases", "mysql", driver="pymysql")
        self.assertIs(cls_2, self.connector_cls)


class TestMongoDBRegistration(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.databases.mongodb as mod
        importlib.reload(mod)
        self.connector_cls = mod.MongoDBConnector

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("databases", "mongodb")
        self.assertIs(cls, self.connector_cls)
        cls_pymongo = registry.get("databases", "mongodb", driver="pymongo")
        self.assertIs(cls_pymongo, self.connector_cls)
        cls_motor = registry.get("databases", "mongodb", driver="motor")
        self.assertIs(cls_motor, self.connector_cls)


class TestRedisRegistration(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.databases.redis as mod
        importlib.reload(mod)
        self.connector_cls = mod.RedisConnector

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("databases", "redis")
        self.assertIs(cls, self.connector_cls)


class TestDatabasesRegistration(unittest.TestCase):
    def test_all_databases_registered(self):
        from uniconnect import registry
        dbs = registry.list_connectors().get("databases", [])
        expected = {
            "sqlite", "postgres", "mysql", "sqlserver", "oracle",
            "mariadb", "mongodb", "redis", "duckdb",
            "memcached", "neo4j", "elasticsearch", "clickhouse",
            "influxdb", "cassandra", "couchbase", "couchdb",
            "dynamodb", "arangodb", "cockroachdb", "singlestore",
            "timescaledb", "yugabytedb", "firebird", "ibm_db2",
            "sap_hana",
        }
        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, dbs, f"{name} not in databases connectors")


if __name__ == "__main__":
    unittest.main()
