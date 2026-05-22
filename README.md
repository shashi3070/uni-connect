# uni-connect

**One API to connect them all — storage, databases, ETL, CRM, AI/LLM, messaging, cloud, and more.**

`uni-connect` is a universal connection manager for Python that provides a single unified interface to 150+ connection types across 13 categories. It features auto-detection from connection strings, multiple driver support, credential management, a pluggable architecture, and both sync/async interfaces on every connector.

```python
from uniconnect import connect

# Auto-detect from URI
s3 = connect("s3://my-bucket?region=us-east-1")
s3.list_files()

# Explicit type with config dict
pg = connect("postgresql://user:pass@localhost:5432/mydb")
pg.query("SELECT * FROM users")

# Context manager
with connect("sqlite", {"path": "test.db"}) as db:
    rows = db.query("SELECT * FROM items")
```

## Installation

```bash
pip install uni-connect
```

Install only what you need:

```bash
pip install "uni-connect[s3,postgres,llm]"
```

Or everything:

```bash
pip install "uni-connect[all]"
```

## Quick Start

```python
from uniconnect import connect

# Storage
s3 = connect("s3", {"aws_access_key_id": "...", "aws_secret_access_key": "...", "region": "us-east-1", "bucket": "my-bucket"})
s3.connect()
s3.list_files(prefix="data/")
s3.close()

# Database
pg = connect("postgres", {"host": "localhost", "database": "mydb", "user": "admin", "password": "pass"})
pg.connect()
results = pg.query("SELECT * FROM users")
pg.close()

# AI / LLM
llm = connect("openai", {"api_key": "sk-...", "model": "gpt-4o"})
llm.connect()
resp = llm.complete([{"role": "user", "content": "Hello"}])
llm.close()

# With context manager
with connect("sqlite", {"path": ":memory:"}) as db:
    db.execute("CREATE TABLE test (id INT)")
    print(db.query("SELECT * FROM test"))
```

## Table of Contents

- [Storage Connectors](#-storage-connectors)
- [Database Connectors](#-database-connectors)
- [Warehouse Connectors](#-warehouse-connectors)
- [ETL Connectors](#-etl-connectors)
- [AI / LLM Connectors](#-ai--llm-connectors)
- [CRM / SaaS Connectors](#-crm--saas-connectors)
- [Messaging Connectors](#-messaging-connectors)
- [Payments Connectors](#-payments-connectors)
- [Cloud Connectors](#-cloud-connectors)
- [Collaboration Connectors](#-collaboration-connectors)
- [Streaming Connectors](#-streaming-connectors)
- [Auth Connectors](#-auth-connectors)
- [BI Connectors](#-bi-connectors)
- [Architecture](#architecture)
- [Why uni-connect?](#why-uni-connect)
- [Contributing](#contributing)
- [License](#license)

---

## Storage Connectors

All storage connectors share a common file-operation API: `list_files()`, `read_file()`, `write_file()`, `delete_file()`, `file_exists()`.

### S3

Drivers: `boto3` (default), `s3fs`, `aioboto3`

```python
from uniconnect import connect

s3 = connect("s3", {
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
    "region": "us-east-1",
    "bucket": "my-bucket",
    "driver": "boto3",           # optional, defaults to boto3
    "endpoint_url": None,        # for S3-compatible storage (MinIO, etc.)
})
s3.connect()

s3.list_files(prefix="data/")        # -> ["data/file1.csv", "data/file2.csv"]
s3.read_file("data/file.csv")        # -> b"content"
s3.write_file("data/file.csv", b"content")
s3.delete_file("data/file.csv")
s3.file_exists("data/file.csv")      # -> True/False
s3.close()
```

### GCS (Google Cloud Storage)

```python
from uniconnect import connect

gcs = connect("gcs", {
    "bucket": "my-bucket",
    "project": "my-project",
    "credentials_path": "/path/to/service-account.json",  # optional, falls back to ADC
})
gcs.connect()
gcs.list_files(prefix="data/")
gcs.read_file("data/file.csv")
gcs.write_file("data/file.csv", b"content")
gcs.delete_file("data/file.csv")
gcs.file_exists("data/file.csv")
gcs.close()
```

### Azure Blob Storage

```python
from uniconnect import connect

blob = connect("azure_blob", {
    "connection_string": "DefaultEndpointsProtocol=...",
    "container_name": "my-container",
})
blob.connect()
blob.list_files(prefix="data/")
blob.read_file("data/file.csv")
blob.write_file("data/file.csv", b"content")
blob.delete_file("data/file.csv")
blob.file_exists("data/file.csv")
blob.close()
```

### FTP / FTPS

```python
from uniconnect import connect

ftp = connect("ftp", {
    "host": "ftp.example.com",
    "port": 21,
    "user": "anonymous",
    "password": "anonymous@",
    "tls": False,                 # set True for FTPS
})
ftp.connect()
ftp.list_files(prefix="/pub")
ftp.read_file("/pub/readme.txt")
ftp.write_file("/tmp/test.txt", b"content")
ftp.delete_file("/tmp/test.txt")
ftp.file_exists("/pub/readme.txt")
ftp.close()
```

### SFTP

Drivers: `paramiko` (default), `pysftp`

```python
from uniconnect import connect

sftp = connect("sftp", {
    "host": "sftp.example.com",
    "port": 22,
    "user": "user",
    "password": "pass",
    "private_key_path": "/path/to/key",    # optional
    "driver": "paramiko",                  # optional
})
sftp.connect()
sftp.list_files(prefix="/remote/path")
sftp.read_file("/remote/path/file.csv")
sftp.write_file("/remote/path/file.csv", b"content")
sftp.delete_file("/remote/path/file.csv")
sftp.file_exists("/remote/path/file.csv")
sftp.close()
```

### Local Filesystem

```python
from uniconnect import connect

local = connect("local", {
    "base_path": "/path/to/directory",
})
local.connect()
local.list_files(prefix="subdir/")
local.read_file("file.txt")
local.write_file("file.txt", b"content")
local.delete_file("file.txt")
local.file_exists("file.txt")
local.close()
```

### MinIO (S3-compatible)

```python
from uniconnect import connect

minio = connect("minio", {
    "endpoint": "play.min.io",
    "access_key": "minioadmin",
    "secret_key": "minioadmin",
    "bucket": "my-bucket",
    "secure": True,
    "region": "us-east-1",
})
minio.connect()
minio.list_files(prefix="data/")
minio.read_file("data/file.csv")
minio.write_file("data/file.csv", b"content")
minio.delete_file("data/file.csv")
minio.file_exists("data/file.csv")
minio.close()
```

### Dropbox (skeleton)

```python
from uniconnect import connect

dropbox = connect("dropbox", {"access_token": "..."})
dropbox.connect()  # raises NotImplementedError — contributions welcome
```

### OneDrive (skeleton)

```python
onedrive = connect("onedrive", {"client_id": "...", "client_secret": "..."})
onedrive.connect()  # raises NotImplementedError
```

### WebDAV (skeleton)

```python
webdav = connect("webdav", {"base_url": "...", "user": "...", "password": "..."})
webdav.connect()  # raises NotImplementedError
```

---

## Database Connectors

Relational databases share `query()` and `execute()`. NoSQL connectors expose their native CRUD methods.

### PostgreSQL

Drivers: `psycopg2` (default), `asyncpg` (async-only)

```python
from uniconnect import connect

pg = connect("postgres", {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "admin",
    "password": "secret",
    "driver": "psycopg2",                      # optional
})
pg.connect()
pg.query("SELECT * FROM users WHERE id = %s", (1,))  # -> [{"id": 1, "name": "Alice"}]
pg.execute("UPDATE users SET name = %s WHERE id = %s", ("Bob", 1))  # -> rowcount
pg.table_exists("users")                              # -> True/False
pg.get_tables()                                       # -> ["users", "orders"]
pg.close()
```

### MySQL

Drivers: `mysql-connector-python` (default), `pymysql`

```python
from uniconnect import connect

mysql = connect("mysql", {
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "user": "root",
    "password": "secret",
    "driver": "mysql-connector-python",
})
mysql.connect()
mysql.query("SELECT * FROM users")
mysql.execute("INSERT INTO users (name) VALUES (%s)", ("Alice",))
mysql.close()
```

### SQL Server

Drivers: `pyodbc` (default), `pymssql`

```python
from uniconnect import connect

mssql = connect("sqlserver", {
    "host": "localhost",
    "port": 1433,
    "database": "mydb",
    "user": "sa",
    "password": "YourPassword123!",
    "driver": "pyodbc",
    "odbc_driver": "ODBC Driver 17 for SQL Server",   # pyodbc only
})
mssql.connect()
mssql.query("SELECT * FROM users")
mssql.execute("UPDATE users SET name = ? WHERE id = ?", ("Bob", 1))
mssql.close()
```

### Oracle

Drivers: `cx_oracle` (default), `oracledb`

```python
from uniconnect import connect

oracle = connect("oracle", {
    "host": "localhost",
    "port": 1521,
    "database": "ORCL",           # SID
    "user": "system",
    "password": "oracle",
    "driver": "cx_oracle",
    "service_name": "",           # alternative to SID
    "dsn": "",                    # fully custom DSN
})
oracle.connect()
oracle.query("SELECT * FROM users")
oracle.execute("UPDATE users SET name = :1 WHERE id = :2", ("Bob", 1))
oracle.close()
```

### SQLite

```python
from uniconnect import connect

# In-memory
sqlite = connect("sqlite", {"path": ":memory:"})
sqlite.connect()
sqlite.query("SELECT sqlite_version()")
sqlite.execute("CREATE TABLE test (id INTEGER, name TEXT)")
sqlite.close()

# File-based
with connect("sqlite", {"path": "data.db"}) as db:
    rows = db.query("SELECT * FROM users")

# URI-based
with connect("sqlite", {"uri": "file:data.db?mode=ro"}) as db:
    rows = db.query("SELECT * FROM users")
```

### MariaDB

```python
from uniconnect import connect

mariadb = connect("mariadb", {
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "user": "root",
    "password": "secret",
})
mariadb.connect()
mariadb.query("SELECT * FROM users")
mariadb.execute("INSERT INTO users (name) VALUES (?)", {"name": "Alice"})
mariadb.close()
```

### CockroachDB (reuses PostgreSQL driver)

```python
from uniconnect import connect

crdb = connect("cockroachdb", {
    "host": "localhost",
    "port": 26257,
    "database": "defaultdb",
    "user": "root",
    "password": "",
})
crdb.connect()
crdb.query("SELECT * FROM users")
crdb.close()
```

### TimescaleDB (reuses PostgreSQL driver)

```python
ts = connect("timescaledb", {
    "host": "localhost", "database": "mydb", "user": "admin", "password": "pass"
})
ts.connect()
ts.query("SELECT * FROM conditions")
ts.close()
```

### YugabyteDB (reuses PostgreSQL driver)

```python
yb = connect("yugabytedb", {"host": "localhost", "port": 5433, "database": "yugabyte", "user": "yugabyte"})
yb.connect()
yb.query("SELECT * FROM users")
yb.close()
```

### MongoDB

Drivers: `pymongo` (default), `motor` (async-only)

```python
from uniconnect import connect

mongo = connect("mongodb", {
    "uri": "mongodb://localhost:27017",
    "database": "mydb",
    "collection": "users",
    "driver": "pymongo",
})
mongo.connect()
mongo.find({"age": {"$gt": 21}})                  # -> list of documents
mongo.find_one({"name": "Alice"})                  # -> dict or None
mongo.insert_one({"name": "Bob", "age": 30})
mongo.insert_many([{"name": "Carol"}, {"name": "Dave"}])
mongo.update_one({"name": "Bob"}, {"$set": {"age": 31}})
mongo.delete_one({"name": "Dave"})
mongo.close()
```

### Redis

```python
from uniconnect import connect

r = connect("redis", {
    "host": "localhost",
    "port": 6379,
    "password": None,
    "db": 0,
})
r.connect()
r.set("key", "value")                  # -> True
r.set("key_exp", "value", ex=60)       # expires in 60s
r.get("key")                            # -> "value"
r.exists("key")                         # -> True
r.delete("key")                         # -> True
r.publish("channel", "message")         # -> subscribers count
r.close()
```

### DuckDB

```python
from uniconnect import connect

# In-memory
duck = connect("duckdb", {"path": ":memory:"})
duck.connect()
duck.query("SELECT 1 + 1 AS result")    # -> [{"result": 2}]
duck.execute("CREATE TABLE t (x INTEGER)")
duck.query("SELECT * FROM t")
duck.close()

# File-based
with connect("duckdb", {"path": "analytics.db"}) as db:
    db.query("SELECT * FROM parquet_scan('data/*.parquet')")
```

### DynamoDB

```python
from uniconnect import connect

dynamo = connect("dynamodb", {
    "region": "us-east-1",
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
    "endpoint_url": None,           # for DynamoDB Local
})
dynamo.connect()
dynamo.get_item("users", {"id": "123"})
dynamo.put_item("users", {"id": "124", "name": "Alice"})
dynamo.delete_item("users", {"id": "124"})
dynamo.query("users", KeyConditionExpression="id = :id", ExpressionAttributeValues={":id": "123"})
dynamo.scan("users")
dynamo.close()
```

### Elasticsearch (skeleton)

```python
es = connect("elasticsearch", {"host": "localhost", "port": 9200})
es.connect()  # install 'elasticsearch' package to use
```

### Neo4j (skeleton)

```python
neo = connect("neo4j", {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "password"})
neo.connect()  # install 'neo4j' package to use
```

### Other database skeletons

These connectors raise `NotImplementedError` until the required driver is installed:

| Connector    | Install                        |
|-------------|--------------------------------|
| ClickHouse  | `clickhouse-driver`            |
| InfluxDB    | `influxdb-client`              |
| Cassandra   | `cassandra-driver`             |
| Couchbase   | `couchbase`                    |
| CouchDB     | `couchdb`                      |
| ArangoDB    | `python-arango`                |
| Memcached   | `pymemcache`                   |
| IBM Db2     | `ibm-db`                       |
| SAP HANA    | `hdbcli`                       |
| SingleStore | `pymysql` or `mysql-connector-python` |
| Firebird    | `fdb`                          |

---

## Warehouse Connectors

### Redshift

Drivers: `psycopg2` (default), `redshift_connector`

```python
from uniconnect import connect

rs = connect("redshift", {
    "host": "my-cluster.xxxxxx.redshift.amazonaws.com",
    "port": 5439,
    "database": "dev",
    "user": "admin",
    "password": "secret",
    "driver": "psycopg2",
})
rs.connect()
rs.query("SELECT * FROM sales")                  # -> list of dicts
rs.execute("DELETE FROM staging WHERE date < '2024-01-01'")  # -> rowcount
rs.copy_from_s3("sales", "s3://bucket/sales.parquet", iam_role="arn:aws:iam::...", region="us-east-1")
rs.close()
```

### Snowflake

```python
from uniconnect import connect

sf = connect("snowflake", {
    "account": "xy12345.us-east-1",
    "user": "admin",
    "password": "secret",
    "warehouse": "COMPUTE_WH",
    "database": "ANALYTICS",
    "schema": "PUBLIC",
})
sf.connect()
sf.query("SELECT * FROM users LIMIT 10")
sf.execute("DELETE FROM staging WHERE loaded = TRUE")
sf.close()
```

### BigQuery

```python
from uniconnect import connect

bq = connect("bigquery", {
    "project": "my-project",
    "credentials_path": "/path/to/service-account.json",   # optional, falls back to ADC
    "dataset": "analytics",                                 # used by load_from_gcs
})
bq.connect()
bq.query("SELECT * FROM `my-project.analytics.users` LIMIT 10")
bq.execute("DELETE FROM `my-project.analytics.staging` WHERE 1=1")
bq.load_from_gcs("users", "gs://bucket/users.csv", source_format="CSV", autodetect=True)
bq.close()
```

### Databricks

Drivers: `databricks-sql-connector` (default, for SQL), `databricks-sdk` (for API)

```python
from uniconnect import connect

db = connect("databricks", {
    "server_hostname": "dbc-xxxxxx.cloud.databricks.com",
    "http_path": "/sql/1.0/warehouses/xxxxxx",
    "access_token": "dapi...",
    "driver": "databricks-sql-connector",
    "warehouse_id": "xxxxxx",             # required for databricks-sdk driver
})
db.connect()
db.query("SELECT * FROM analytics.users LIMIT 10")
db.execute("DELETE FROM staging WHERE date < '2024-01-01'")
db.close()
```

### Athena

```python
from uniconnect import connect

athena = connect("athena", {
    "region": "us-east-1",
    "database": "analytics",
    "s3_output_location": "s3://my-bucket/athena-results/",
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
})
athena.connect()
results = athena.query("SELECT * FROM users LIMIT 10")
athena.close()
```

### Presto / Trino

```python
presto = connect("presto", {
    "host": "localhost", "port": 8080, "user": "admin",
    "catalog": "hive", "schema": "default",
})
presto.connect()
presto.query("SELECT * FROM hive.default.users")
presto.close()

# Also registered as "trino"
trino = connect("trino", {"host": "localhost", "port": 8080})
trino.connect()
```

### Hive

```python
hive = connect("hive", {
    "host": "localhost", "port": 10000, "user": "hive",
    "database": "default", "auth": "NONE",
})
hive.connect()
hive.query("SELECT * FROM users")
hive.close()
```

### Impala

```python
impala = connect("impala", {
    "host": "localhost", "port": 21050, "user": "",
    "database": "default", "auth_mechanism": "PLAIN",
})
impala.connect()
impala.query("SELECT * FROM users")
impala.close()
```

### Druid

```python
druid = connect("druid", {
    "host": "localhost", "port": 8888, "path": "/druid/v2/sql",
})
druid.connect()
druid.query("SELECT COUNT(*) FROM wikipedia")
druid.close()
```

### Pinot

```python
pinot = connect("pinot", {
    "host": "localhost", "port": 8099, "path": "/query/sql",
})
pinot.connect()
pinot.query("SELECT * FROM airlineStats LIMIT 10")
pinot.close()
```

---

## ETL Connectors

### Matillion

```python
from uniconnect import connect

mat = connect("matillion", {
    "base_url": "https://my-matillion-instance.com",
    "api_key": "your-api-key",
    "project_id": "my-project",
    "environment_name": "Production",
})
mat.connect()
mat.list_jobs()                                             # -> list of jobs
mat.run_job("Load Customers")                               # -> run result
mat.get_job_status("run-123")                               # -> run status
mat.close()
```

### Fivetran

```python
from uniconnect import connect

fiv = connect("fivetran", {
    "api_key": "your-api-key",
    "api_secret": "your-api-secret",
})
fiv.connect()
fiv.list_connectors()               # -> list of connectors
fiv.list_destinations()             # -> list of destinations
fiv.sync("connector_123")           # -> trigger sync
fiv.close()
```

### Airbyte

```python
from uniconnect import connect

ab = connect("airbyte", {
    "host": "localhost",
    "port": 8001,
    "api_key": "",                  # optional
})
ab.connect()
ab.list_workspaces()                # -> list of workspaces
ab.list_sources()                   # -> list of sources
ab.list_destinations()              # -> list of destinations
ab.sync("connection-123")           # -> trigger sync
ab.close()
```

### dbt Cloud

```python
from uniconnect import connect

dbt = connect("dbt", {
    "api_url": "https://cloud.getdbt.com/api/v2",
    "service_token": "dbtpts_...",
    "account_id": "12345",
})
dbt.connect()
dbt.list_jobs()                     # -> list of jobs
dbt.run_job("67890")                # -> run result
dbt.get_run_status("run-12345")     # -> run status
dbt.close()
```

### Stitch

```python
stitch = connect("stitch", {
    "client_id": "1234",
    "access_token": "your-access-token",
})
stitch.connect()
stitch.list_sources()
stitch.list_extractions()
stitch.close()
```

### Talend

```python
talend = connect("talend", {
    "base_url": "https://api.talend.com",
    "api_token": "your-token",
})
talend.connect()
talend.list_executables()
talend.run_executable("exec-123")
talend.close()
```

### Informatica

```python
inf = connect("informatica", {
    "base_url": "https://api.informatica.cloud",
    "username": "user@example.com",
    "password": "secret",
})
inf.connect()
inf.list_connections()
inf.close()
```

### NiFi

```python
nifi = connect("nifi", {
    "host": "localhost",
    "port": 8080,
    "username": "",              # optional
    "password": "",              # optional
})
nifi.connect()
nifi.list_process_groups()
nifi.list_processors("root")
nifi.close()
```

---

## AI / LLM Connectors

All LLM connectors share `complete(messages, **kwargs)`. Many also support `stream_complete()`.

### OpenAI

Driver `azure` available for Azure OpenAI.

```python
from uniconnect import connect

# Standard OpenAI
llm = connect("openai", {
    "api_key": "sk-...",
    "model": "gpt-4o",
    "base_url": None,                       # optional, for proxy
})
llm.connect()

# Chat completion
resp = llm.complete([{"role": "user", "content": "Hello"}])
# -> {"choices": [{"message": {"content": "Hi!"}}], ...}

# Streaming
for chunk in llm.stream_complete([{"role": "user", "content": "Tell me a story"}]):
    print(chunk["choices"][0]["delta"].get("content", ""))

# Embeddings
embeddings = llm.embed(["Hello world", "How are you?"])
# -> [[0.012, ...], [0.034, ...]]

# List models
models = llm.models()
# -> ["gpt-4o", "gpt-4-turbo", ...]

llm.close()

# Azure OpenAI
azure = connect("openai", {
    "api_key": "...",
    "base_url": "https://my-resource.openai.azure.com",
    "model": "gpt-4o",
    "azure": True,
    "api_version": "2024-02-15-preview",
})
azure.connect()
resp = azure.complete([{"role": "user", "content": "Hello"}])
azure.close()
```

### Anthropic (Claude)

```python
from uniconnect import connect

claude = connect("anthropic", {
    "api_key": "sk-ant-...",
    "model": "claude-sonnet-4-20250514",
    "base_url": None,                       # optional
})
claude.connect()
resp = claude.complete([{"role": "user", "content": "Hello"}])
# -> {"content": [{"text": "Hi!"}], ...}

for chunk in claude.stream_complete([{"role": "user", "content": "Tell me a story"}]):
    print(chunk.get("delta", {}).get("text", ""))

claude.close()
```

### Google AI (Gemini)

```python
from uniconnect import connect

gemini = connect("google_ai", {
    "api_key": "AIza...",
    "model": "gemini-pro",
})
gemini.connect()
resp = gemini.complete([{"role": "user", "content": "Hello"}])
# -> {"text": "Hi!", "candidates": [...]}

for chunk in gemini.stream_complete([{"role": "user", "content": "Story time"}]):
    print(chunk["text"])

# Image generation
img = gemini.generate_image("A cat wearing a hat", image_model="imagen-3.0-generate-001")
gemini.close()
```

### AWS Bedrock

```python
from uniconnect import connect

bedrock = connect("bedrock", {
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
    "region": "us-east-1",
    "model_id": "anthropic.claude-v2",
})
bedrock.connect()
resp = bedrock.complete([{"role": "user", "content": "Hello"}])
bedrock.close()
```

### Ollama (local LLMs)

```python
from uniconnect import connect

ollama = connect("ollama", {
    "base_url": "http://localhost:11434",
    "model": "llama3",
})
ollama.connect()
resp = ollama.complete([{"role": "user", "content": "Hello"}])
for chunk in ollama.stream_complete([{"role": "user", "content": "Story time"}]):
    print(chunk["message"]["content"])

ollama.list_models()          # -> [{"name": "llama3:latest", ...}]
ollama.pull_model("mistral")  # -> pull result
ollama.close()
```

### Groq

OpenAI-compatible, uses `openai` package.

```python
from uniconnect import connect

groq = connect("groq", {
    "api_key": "gsk_...",
    "model": "llama3-70b-8192",
    "base_url": "https://api.groq.com/openai/v1",  # default
})
groq.connect()
resp = groq.complete([{"role": "user", "content": "Hello"}])
groq.close()
```

### DeepSeek

OpenAI-compatible, uses `openai` package.

```python
from uniconnect import connect

ds = connect("deepseek", {
    "api_key": "sk-...",
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com",        # default
})
ds.connect()
resp = ds.complete([{"role": "user", "content": "Hello"}])
ds.close()
```

### Mistral AI

```python
from uniconnect import connect

mistral = connect("mistral", {
    "api_key": "...",
    "model": "mistral-large-latest",
    "server_url": None,          # optional
})
mistral.connect()
resp = mistral.complete([{"role": "user", "content": "Hello"}])
mistral.close()
```

### Replicate

```python
from uniconnect import connect

rep = connect("replicate", {
    "api_token": "r8_...",
    "model": "meta/meta-llama-3-70b-instruct",
})
rep.connect()
output = rep.run({"prompt": "Hello"})
rep.close()
```

### Hugging Face

```python
from uniconnect import connect

hf = connect("huggingface", {
    "api_token": "hf_...",          # optional for public models
    "model": "gpt2",                # used with InferenceClient
    "endpoint_url": None,           # optional, for dedicated endpoints
})
hf.connect()
result = hf.inference("Hello, my name is")
# -> [{"generated_text": "..."}]

hf.list_models(task="text-generation")   # -> ["gpt2", ...]
hf.close()
```

### Skeleton AI connectors

These OpenAI-compatible connectors raise `NotImplementedError`:

| Connector    | Compatible with |
|-------------|----------------|
| `vllm`      | OpenAI API      |
| `llama_cpp` | OpenAI API      |
| `together`  | OpenAI API      |
| `fireworks` | OpenAI API      |
| `perplexity`| OpenAI API      |
| `cohere`    | Cohere API      |
| `mlflow`    | MLflow Gateway  |

---

## CRM / SaaS Connectors

### Salesforce

Drivers: `simple_salesforce` (default), `pysfdc`

```python
from uniconnect import connect

sf = connect("salesforce", {
    "username": "user@example.com",
    "password": "password123",
    "security_token": "your_token",
    "domain": "login",                    # "test" for sandbox
    "driver": "simple_salesforce",
})
sf.connect()

# SOQL query
sf.query("SELECT Id, Name, Type FROM Account")

# CRUD on any SObject
sf.describe("Account")
sf.create("Account", {"Name": "New Account", "Type": "Customer"})
sf.update("Account", "001xx000003DGbA", {"Name": "Updated"})
sf.delete("Account", "001xx000003DGbA")
sf.close()
```

### HubSpot

```python
from uniconnect import connect

hub = connect("hubspot", {
    "access_token": "pat-...",
})
hub.connect()
hub.get_contacts()              # -> list of contacts
hub.get_deals()                 # -> list of deals
hub.create_contact({"email": "alice@example.com", "firstname": "Alice"})
hub.close()
```

### Other CRM skeletons

Zoho, Pipedrive, Zendesk, Freshdesk, Intercom, Marketo, MS Dynamics, NetSuite, SAP CRM, ServiceNow, SugarCRM — all raise `NotImplementedError`.

---

## Messaging Connectors

### SMTP

```python
from uniconnect import connect

email = connect("email_smtp", {
    "host": "smtp.gmail.com",
    "port": 587,
    "user": "you@gmail.com",
    "password": "app-password",
    "use_tls": True,
    "from_name": "Your Name",
})
email.connect()

# Plain text
email.send(to="user@example.com", subject="Hello", body="World")

# HTML with attachment
email.send(
    to=["alice@example.com", "bob@example.com"],
    subject="Report",
    body="See attached",
    html="<h1>Report</h1><p>See attached</p>",
    attachments=[
        {"path": "/path/to/report.pdf", "filename": "report.pdf"},
    ],
)
email.close()
```

### IMAP

```python
from uniconnect import connect

imap = connect("email_imap", {
    "host": "imap.gmail.com",
    "port": 993,
    "user": "you@gmail.com",
    "password": "app-password",
})
imap.connect()
imap.list_mailboxes()               # -> ["INBOX", "Sent", ...]
imap.fetch_messages("INBOX", 5)     # -> [{id, subject, from, date}, ...]
imap.search("UNSEEN")               # -> ["123", "124", ...]
imap.close()
```

### SendGrid

```python
from uniconnect import connect

sg = connect("sendgrid", {
    "api_key": "SG.xxxx",
    "from_email": "noreply@example.com",
})
sg.connect()
sg.send(to="user@example.com", subject="Hello", body="World")
sg.send(to=["a@b.com", "c@d.com"], subject="Hello", body="World", html="<p>World</p>")
sg.close()
```

### Mailgun

```python
from uniconnect import connect

mg = connect("mailgun", {
    "api_key": "key-xxxx",
    "domain": "mg.example.com",
    "from_email": "noreply@mg.example.com",
})
mg.connect()
mg.send(to="user@example.com", subject="Hello", body="World")
mg.close()
```

### Slack

```python
from uniconnect import connect

slack = connect("slack", {
    "token": "xoxb-...",
})
slack.connect()
slack.post_message("#general", "Hello from uni-connect!")
slack.list_channels()                    # -> [{name, id, ...}]
slack.upload_file("#general", "/path/to/report.pdf")
slack.close()
```

### Twilio

```python
from uniconnect import connect

twilio = connect("twilio", {
    "account_sid": "AC...",
    "auth_token": "your-auth-token",
    "from_number": "+1234567890",
})
twilio.connect()
twilio.send_sms("+1987654321", "Hello from Python!")       # SMS
twilio.send_whatsapp("+1987654321", "Hello via WhatsApp")  # WhatsApp
twilio.close()
```

### Skeleton messaging connectors

Discord, Teams, Telegram, Pushbullet, OneSignal, FCM, Mailchimp — all raise `NotImplementedError`.

---

## Payments Connectors

### Stripe

```python
from uniconnect import connect

stripe = connect("stripe", {
    "api_key": "sk_live_...",
})
stripe.connect()
stripe.list_products()                                       # -> paginated products
stripe.list_customers()                                      # -> paginated customers
stripe.create_payment_intent(amount=2000, currency="usd")   # -> payment intent
stripe.close()
```

### Skeleton payment connectors

Shopify, WooCommerce, Braintree — all raise `NotImplementedError`.

---

## Cloud Connectors

### AWS

```python
from uniconnect import connect

aws = connect("aws", {
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
    "region": "us-east-1",
})
aws.connect()
aws.list_s3_buckets()                     # -> [{Name: "my-bucket", ...}]
aws.list_lambda_functions()               # -> [{FunctionName: "my-func", ...}]
aws.list_sqs_queues()                     # -> ["https://sqs.us-east-1.amazonaws.com/..."]
aws.send_sqs_message("https://sqs...", "Hello")
aws.invoke_lambda("my-func", '{"key": "value"}')

# Generic service client
s3 = aws.get_client("s3")
ec2 = aws.get_client("ec2")
aws.close()
```

### GCP

```python
from uniconnect import connect

gcp = connect("gcp", {
    "credentials_path": "/path/to/service-account.json",   # optional
    "project": "my-project",
})
gcp.connect()
gcp.list_pubsub_topics()                                    # -> ["projects/.../topics/..."]
gcp.publish_pubsub("my-topic", "Hello World")

# Generic service client
compute = gcp.get_client("compute", version="v1")
gcp.close()
```

### Azure

```python
from uniconnect import connect

azure = connect("azure", {
    "tenant_id": "your-tenant-id",
    "client_id": "your-client-id",           # optional, uses DefaultAzureCredential if omitted
    "client_secret": "your-client-secret",   # optional
    "subscription_id": "your-sub-id",
})
azure.connect()

# Generic service client
resource = azure.get_client("resource")
azure.close()
```

### Kubernetes

```python
from uniconnect import connect

k8s = connect("kubernetes", {})
k8s.connect()           # loads ~/.kube/config
k8s.list_pods("default")
k8s.get_logs("my-pod", "default")
k8s.close()
```

### Docker

```python
from uniconnect import connect

docker = connect("docker", {
    "base_url": None,          # optional, defaults to DOCKER_HOST env or local socket
})
docker.connect()
docker.list_containers(all=False)           # -> list of container attrs
docker.run_container("nginx:latest", detach=True)
docker.close()
```

### HashiCorp Vault

```python
from uniconnect import connect

vault = connect("vault", {
    "url": "https://vault.example.com",
    "token": "hvs.xxx",                # token-based auth
    # "role_id": "...",                # or approle auth
    # "secret_id": "...",
})
vault.connect()
vault.read_secret("my-secret", mount_point="secret")     # -> {"key": "value"}
vault.write_secret("my-secret", {"key": "value"})
vault.list_secrets("", mount_point="secret")              # -> ["my-secret"]
vault.close()
```

### Terraform (skeleton)

```python
tf = connect("terraform", {"token": "..."})
tf.connect()  # raises NotImplementedError
```

---

## Collaboration Connectors

### GitHub

```python
from uniconnect import connect

gh = connect("github", {
    "token": "ghp_...",
    "owner": "my-org",            # optional, needed for repo operations
    "repo": "my-repo",            # optional
})
gh.connect()
gh.list_repos()                          # -> [{name, full_name, url}, ...]
gh.get_file("path/to/file.py", ref="main")
gh.create_issue("Bug found", "Details here")
gh.list_issues(state="open")
gh.close()
```

### Jira

```python
from uniconnect import connect

jira = connect("jira", {
    "url": "https://my-company.atlassian.net",
    "username": "user@example.com",
    "api_token": "your-api-token",
})
jira.connect()
jira.create_issue("PROJ", "Fix login bug", "Details here", issuetype="Bug")
jira.search_issues("project = PROJ AND status = 'In Progress'")
jira.get_issue("PROJ-123")
jira.close()
```

### Skeleton collaboration connectors

GitLab, Bitbucket, Confluence, Notion, Linear — all raise `NotImplementedError`.

---

## Streaming Connectors

### Kafka

```python
from uniconnect import connect

kafka = connect("kafka", {
    "bootstrap_servers": "localhost:9092",
    "group_id": "my-group",             # optional, for consumer
})
kafka.connect()

# Produce
kafka.produce("my-topic", "Hello Kafka", key="msg1")

# Consume (creates a temporary consumer)
messages = kafka.consume("my-topic", timeout=2.0)
# -> [{"key": "msg1", "value": "Hello Kafka", "partition": 0, "offset": 0}]

# List topics
kafka.list_topics()
kafka.close()
```

### RabbitMQ

```python
from uniconnect import connect

rmq = connect("rabbitmq", {
    "host": "localhost",
    "port": 5672,
    "user": "guest",
    "password": "guest",
    "virtual_host": "/",
})
rmq.connect()
rmq.declare_queue("my-queue", durable=True)
rmq.publish("my-queue", "Hello RabbitMQ")
rmq.consume("my-queue", callback=lambda msg: print(msg))
rmq.close()
```

### SQS

```python
from uniconnect import connect

sqs = connect("sqs", {
    "region": "us-east-1",
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
    "queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue",
})
sqs.connect()
sqs.send("Hello SQS")
messages = sqs.receive(max_messages=5, wait_time=2)
for msg in messages:
    print(msg["Body"])
    sqs.delete(msg["ReceiptHandle"])
sqs.close()
```

### Skeleton streaming connectors

Google Pub/Sub, Azure Event Hubs, NATS, ZeroMQ — all raise `NotImplementedError`.

---

## Auth Connectors

### OAuth2

```python
from uniconnect import connect

oauth = connect("oauth2", {
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "authorization_url": "https://provider.com/oauth/authorize",
    "token_url": "https://provider.com/oauth/token",
    "scopes": ["openid", "profile", "email"],
})
oauth.connect()

# Step 1: Get authorization URL (redirect user here)
auth_url = oauth.get_authorization_url(
    redirect_uri="https://myapp.com/callback",
    state="random-state-string",
)
# -> "https://provider.com/oauth/authorize?client_id=...&response_type=code&..."

# Step 2: Exchange code for token (in your callback handler)
token = oauth.exchange_code(
    code="code-from-callback",
    redirect_uri="https://myapp.com/callback",
)
# -> {"access_token": "...", "refresh_token": "...", "expires_in": 3600, ...}

# Step 3: Refresh token when expired
new_token = oauth.refresh_token()
# -> updated token dict

# Get current token
current = oauth.get_token()
oauth.close()
```

---

## BI Connectors

BI connectors are skeletons and raise `NotImplementedError`:

```python
tableau = connect("tableau", {"server": "...", "token": "..."})
powerbi = connect("powerbi", {"client_id": "...", "client_secret": "..."})
looker = connect("looker", {"base_url": "...", "client_id": "...", "client_secret": "..."})
mode = connect("mode", {"token": "..."})
metabase = connect("metabase", {"url": "...", "username": "...", "password": "..."})
```

Supported BI connectors (all skeletons): **Tableau, Power BI, Looker, Mode, Metabase**.

---

## Architecture

```
uniconnect/
├── __init__.py           # Public API: connect(), get_connector()
├── core/
│   ├── base.py           # BaseConnector, SyncConnector, AsyncConnector
│   ├── registry.py       # Connector registry (category → name → class)
│   ├── factory.py        # ConnectionFactory: URI + config → connector instance
│   ├── config.py         # Config resolution: env → .env → direct
│   └── exceptions.py     # ConnectionError, ConfigurationError
├── connectors/
│   ├── storage/          # S3, GCS, AzureBlob, FTP, SFTP, Local, MinIO, ...
│   ├── databases/        # PostgreSQL, MySQL, SQLServer, Oracle, SQLite, ...
│   ├── warehouse/        # Redshift, Snowflake, BigQuery, Databricks, ...
│   ├── etl/              # Matillion, Fivetran, Airbyte, dbt, Stitch, ...
│   ├── ai/               # OpenAI, Anthropic, GoogleAI, Bedrock, Ollama, ...
│   ├── crm/              # Salesforce, HubSpot, ...
│   ├── messaging/        # SMTP, IMAP, SendGrid, Mailgun, Slack, Twilio, ...
│   ├── payments/         # Stripe, ...
│   ├── cloud/            # AWS, GCP, Azure, Kubernetes, Docker, Vault, ...
│   ├── collaboration/    # GitHub, Jira, ...
│   ├── streaming/        # Kafka, RabbitMQ, SQS, ...
│   └── auth/             # OAuth2, LDAP, Active Directory
├── utils/
│   ├── retry.py          # Retry/backoff utilities
│   ├── credentials.py    # Credential resolution chain
│   ├── pooling.py        # Connection pooling
│   └── health.py         # Health-check utilities
```

### How it works

1. `connect()` receives a URI string, dict, or type name.
2. `ConnectionFactory` merges config with env variables and credentials.
3. `_identify_connector()` resolves the type via URI scheme detection or the registry.
4. The appropriate connector class is instantiated with the merged config.
5. `connector.connect()` establishes the connection.

---

## Why uni-connect?

- **Most comprehensive catalog**: 150+ connector variants under one roof
- **Multiple drivers**: S3 via boto3, s3fs, or aioboto3; SFTP via paramiko or pysftp; PostgreSQL via psycopg2 or asyncpg; and many more
- **Auto-detection**: Pass a connection string, we figure out the connector type
- **Sync + Async**: Dual interface on every connector (SyncConnector / AsyncConnector)
- **Credential management**: Auto-resolve from env vars → .env → Vault → AWS Secrets → direct config
- **Plugin architecture**: Add custom connectors without modifying core
- **Connection pooling + health checks**: Built into every connector
- **Context manager support**: Every connector works with `with` blocks
- **Uniform API**: Same patterns across radically different services

---

## Contributing

Adding a new connector is straightforward:

1. Create a class inheriting from `SyncConnector` or `AsyncConnector` in the appropriate category under `uniconnect/connectors/`.
2. Implement `connect()`, `close()`, and your service-specific methods.
3. Register with the registry:
   ```python
   from uniconnect.core.registry import registry
   registry.register("category", "my_connector", MyConnector)
   registry.register("category", "my_connector", MyConnector, driver="driver_name")  # for driver variants
   ```
4. Add the connector to `setup.py` extras if it has third-party dependencies.
5. Done! `connect("my_connector", {...})` will now work.

---

## License

MIT
