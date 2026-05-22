import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


class TestOpenAIConnector(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.ai.openai as mod
        importlib.reload(mod)
        self.connector_cls = mod.OpenAIConnector

    def test_init(self):
        conn = self.connector_cls(config={"api_key": "sk-test"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["api_key"], "sk-test")

    def test_missing_driver(self):
        conn = self.connector_cls(config={"api_key": "sk-test"})
        with patch.dict('sys.modules', {'openai': None}):
            import importlib
            import uniconnect.connectors.ai.openai as mod
            importlib.reload(mod)
            conn2 = mod.OpenAIConnector(config={"api_key": "sk-test"})
            with self.assertRaises(ImportError):
                conn2.connect()

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("ai", "openai")
        self.assertIs(cls, self.connector_cls)
        cls_azure = registry.get("ai", "openai", driver="azure")
        self.assertIs(cls_azure, self.connector_cls)


class TestAnthropicConnector(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.ai.anthropic as mod
        importlib.reload(mod)
        self.connector_cls = mod.AnthropicConnector

    def test_init(self):
        conn = self.connector_cls(config={"api_key": "sk-ant-test"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["api_key"], "sk-ant-test")

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("ai", "anthropic")
        self.assertIs(cls, self.connector_cls)


class TestOllamaConnector(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.ai.ollama as mod
        importlib.reload(mod)
        self.connector_cls = mod.OllamaConnector

    def test_init(self):
        conn = self.connector_cls(config={"base_url": "http://localhost:11434"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["base_url"], "http://localhost:11434")

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("ai", "ollama")
        self.assertIs(cls, self.connector_cls)

    def test_connect(self):
        conn = self.connector_cls(config={})
        conn.connect()
        self.assertTrue(conn.is_connected)
        conn.close()
        self.assertFalse(conn.is_connected)


class TestGoogleAIConnector(unittest.TestCase):
    def setUp(self):
        import importlib
        from uniconnect.core.registry import registry
        import uniconnect.connectors.ai.google_ai as mod
        importlib.reload(mod)
        self.connector_cls = mod.GoogleAIConnector

    def test_init(self):
        conn = self.connector_cls(config={"api_key": "AIza-test"})
        self.assertIsNotNone(conn)
        self.assertEqual(conn.config["api_key"], "AIza-test")

    def test_registration(self):
        from uniconnect.core.registry import registry
        cls = registry.get("ai", "google_ai")
        self.assertIs(cls, self.connector_cls)


class TestOtherAIConnectors(unittest.TestCase):
    def test_all_ai_registered(self):
        from uniconnect import registry
        ai = registry.list_connectors().get("ai", [])
        expected = {
            "openai", "anthropic", "google_ai", "bedrock", "ollama",
            "llama_cpp", "vllm", "groq", "deepseek", "mistral",
            "cohere", "together", "replicate", "huggingface",
            "fireworks", "perplexity", "mlflow",
        }
        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, ai, f"{name} not in ai connectors")


class TestBedrockConnector(unittest.TestCase):
    def test_registration(self):
        from uniconnect import registry
        cls = registry.get("ai", "bedrock")
        self.assertIsNotNone(cls)
        conn = cls(config={"region": "us-east-1"})
        self.assertEqual(conn.config["region"], "us-east-1")


class TestAIInitSmoke(unittest.TestCase):
    def test_connectors_can_be_instantiated(self):
        from uniconnect import registry
        ai = registry.list_connectors().get("ai", {})
        for name in ai:
            with self.subTest(name=name):
                cls = registry.get("ai", name)
                conn = cls(config={})
                self.assertIsNotNone(conn)


if __name__ == "__main__":
    unittest.main()
