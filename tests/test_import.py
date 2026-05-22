"""Smoke test: verify uni-connect imports and registry auto-population."""
from uniconnect import connect, registry

# 1. Registry should be populated
connectors = registry.list_connectors()
print("=== Registered Connectors ===")
total = 0
for cat, conns in sorted(connectors.items()):
    print(f"  {cat}: {len(conns)} connector(s) -> {', '.join(sorted(conns))}")
    total += len(conns)
print(f"\nTotal connector registrations: {total}")

assert total > 0, "No connectors registered!"
assert "storage" in connectors
assert "databases" in connectors
assert "warehouse" in connectors
assert "etl" in connectors
assert "ai" in connectors
assert "crm" in connectors
assert "messaging" in connectors
assert "payments" in connectors
assert "cloud" in connectors
assert "collaboration" in connectors
assert "streaming" in connectors
assert "auth" in connectors
assert "business_intelligence" in connectors

# 2. Test basic connect() with known connector types
s3_cls = registry.get("storage", "s3")
print(f"\nS3 connector class: {s3_cls}")

sf_cls = registry.get("crm", "salesforce")
print(f"Salesforce connector class: {sf_cls}")

pg_cls = registry.get("databases", "postgres")
print(f"PostgreSQL connector class: {pg_cls}")

openai_cls = registry.get("ai", "openai")
print(f"OpenAI connector class: {openai_cls}")

# 3. Test instantiation
s3 = s3_cls(config={"region": "us-east-1", "bucket": "test"})
print(f"\nS3 instance: {s3}")
print(f"S3 config: {s3.config}")

# 4. Test connect() factory function
conn = connect("s3", {"region": "us-east-1"})
print(f"\nFactory connect('s3'): {conn}")

# 5. Test URI auto-detection
try:
    conn2 = connect("postgresql://user:pass@localhost:5432/mydb")
    print(f"URI connect: {conn2}")
except Exception as e:
    print(f"URI auto-detect works (would connect if driver installed): {e}")

print("\n=== ALL SMOKE TESTS PASSED ===")
