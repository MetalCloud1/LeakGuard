import os
import sys
import json
import boto3
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import logging

# Add src directory to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)
from src.database import Base
import src.models

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

# === Load secrets ===
# Prefer AWS Secrets Manager
secret_name = os.getenv("AWS_SECRET_NAME")
region_name = os.getenv("AWS_REGION")

secret = {}

if secret_name and region_name:
    try:
        client = boto3.client("secretsmanager", region_name=region_name)
        secret_value = client.get_secret_value(SecretId=secret_name)
        raw = secret_value.get("SecretString", "") or ""
        clean = raw.lstrip("\ufeff").replace("ï»¿", "").strip()
        secret = json.loads(clean)
    except Exception:
        # fallback to loose parse
        def _loose_parse(s: str):
            pairs = [p for p in s.strip().lstrip("{").rstrip("}").split(",") if ":" in p]
            d = {}
            for p in pairs:
                k, v = p.split(":", 1)
                d[k.strip().strip('"').strip("'")] = v.strip().strip('"').strip("'")
            return d
        try:
            secret = _loose_parse(clean)
        except Exception as e:
            raise RuntimeError(
                "Cannot parse secret from AWS Secrets Manager. "
                "Check SecretString is valid JSON."
            ) from e

# Fallback to local secret.json if AWS not configured
if not secret:
    local_secret_file = os.path.join(os.path.dirname(__file__), "secret.json")
    if os.path.exists(local_secret_file):
        with open(local_secret_file, "r") as f:
            secret = json.load(f)
    else:
        secret = {
            "username": os.getenv("DB_USERNAME"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "db_name": os.getenv("DB_NAME"),
        }

# Ensure port is int
if "port" in secret:
    try:
        secret["port"] = int(secret["port"])
    except Exception:
        pass

DATABASE_URL = (
    f"postgresql+psycopg2://{secret['username']}:{secret['password']}"
    f"@{secret['host']}:{secret['port']}/{secret['db_name']}"
)

# Alembic migration functions
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
