# -----------------------------------------------------------------------------  
# Gilbert Ramirez GitHub: https://github.com/MetalCloud1  
# -----------------------------------------------------------------------------  
import os
import boto3
import json
from src.models import User
from src.utils import verify_password
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.future import select
from typing import Optional

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_secret_key():
    environment = os.getenv("ENVIRONMENT", "development")

    if environment == "production":
        secret_name = os.getenv("AWS_SECRET_NAME", "auth-service/prod")
        region_name = os.getenv("AWS_REGION", "us-west-2")

        client = boto3.client("secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response["SecretString"])
        return secret["SECRET_KEY"]
    else:

        return os.getenv("SECRET_KEY", "dummy_dev_key")


async def get_user_by_username(db, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def authenticate_user(db, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    SECRET_KEY = get_secret_key()
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token_return_username(token: str) -> Optional[str]:
    SECRET_KEY = get_secret_key()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        return username
    except JWTError:
        return None
