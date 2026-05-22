import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


class TestRedshiftRegistration(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.warehouse.redshift as mod
        importlib.reload(mod)
        self.connector_cls = mod.RedshiftConnector

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("warehouse", "redshift")
        self.assertIs(cls, self.connector_cls)
        cls_1 = registry.get("warehouse", "redshift", driver="psycopg2")
        self.assertIs(cls_1, self.connector_cls)
        cls_2 = registry.get("warehouse", "redshift", driver="redshift_connector")
        self.assertIs(cls_2, self.connector_cls)

    def test_init(self):
        conn = self.connector_cls(config={
            "host": "redshift-cluster.amazonaws.com",
            "database": "dev",
            "user": "admin",
            "password": "pass",
        })
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["database"], "dev")


class TestSnowflakeRegistration(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.warehouse.snowflake as mod
        importlib.reload(mod)
        self.connector_cls = mod.SnowflakeConnector

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("warehouse", "snowflake")
        self.assertIs(cls, self.connector_cls)

    def test_init(self):
        conn = self.connector_cls(config={"account": "myaccount", "user": "admin", "password": "pass"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["account"], "myaccount")


class TestBigQueryRegistration(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.warehouse.bigquery as mod
        importlib.reload(mod)
        self.connector_cls = mod.BigQueryConnector

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("warehouse", "bigquery")
        self.assertIs(cls, self.connector_cls)

    def test_init(self):
        conn = self.connector_cls(config={"project": "my-project"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["project"], "my-project")


class TestDatabricksRegistration(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.warehouse.databricks as mod
        importlib.reload(mod)
        self.connector_cls = mod.DatabricksConnector

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("warehouse", "databricks")
        self.assertIs(cls, self.connector_cls)
        cls_1 = registry.get("warehouse", "databricks", driver="databricks-sql-connector")
        self.assertIs(cls_1, self.connector_cls)
        cls_2 = registry.get("warehouse", "databricks", driver="databricks-sdk")
        self.assertIs(cls_2, self.connector_cls)

    def test_init(self):
        conn = self.connector_cls(config={
            "server_hostname": "dbc-123.cloud.databricks.com",
            "http_path": "/sql/1.0/warehouses/abc",
            "access_token": "dapi...",
        })
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["server_hostname"], "dbc-123.cloud.databricks.com")


class TestAthenaRegistration(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.warehouse.athena as mod
        importlib.reload(mod)
        self.connector_cls = mod.AthenaConnector

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("warehouse", "athena")
        self.assertIs(cls, self.connector_cls)

    def test_init(self):
        conn = self.connector_cls(config={
            "region": "us-east-1",
            "database": "default",
            "s3_output_location": "s3://results/",
        })
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["region"], "us-east-1")


class TestWarehouseRegistration(unittest.TestCase):
    def test_all_warehouse_registered(self):
        from uniconnect import registry
        wh = registry.list_connectors().get("warehouse", [])
        expected = {"redshift", "snowflake", "bigquery", "databricks", "athena", "presto", "druid", "pinot", "hive", "impala"}
        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, wh, f"{name} not in warehouse connectors")


if __name__ == "__main__":
    unittest.main()
