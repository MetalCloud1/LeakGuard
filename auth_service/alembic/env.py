import os
import sys
import json
import boto3
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
    )
from src.database import Base
import src.models 
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

secret_name = os.getenv("AWS_SECRET_NAME", "auth-service/dev")
region_name = os.getenv("AWS_REGION", "us-west-2")

client = boto3.client("secretsmanager", region_name=region_name)
secret_value = client.get_secret_value(SecretId=secret_name)


raw = secret_value.get("SecretString", "") or ""


clean = raw.lstrip("\ufeff").replace("ï»¿", "").strip()


try:
    secret = json.loads(clean)
except Exception as e:
    def _loose_parse(s: str):
        pairs = [p for p in s.strip().lstrip("{").rstrip("}").split(",") if ":" in p]
        d = {}
        for p in pairs:
            k, v = p.split(":", 1)
            d[k.strip().strip('"').strip("'")] = v.strip().strip('"').strip("'")
        return d

    try:
        secret = _loose_parse(clean)
    except Exception:
        raise RuntimeError(
            "No se pudo parsear el secret desde Secrets Manager. "
            "Verifica el SecretString en AWS y que esté en JSON válido."
        ) from e

if "port" in secret:
    try:
        secret["port"] = int(secret["port"])
    except Exception:
        pass


DATABASE_URL = (
f"postgresql+psycopg2://{secret['username']}:{secret['password']}"
f"@{secret['host']}:{secret['port']}/{secret['db_name']}"
)


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
