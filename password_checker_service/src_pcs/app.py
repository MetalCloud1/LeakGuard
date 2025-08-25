from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import hashlib
import json
import os
import requests
from typing import Optional

app = FastAPI(title="Password Leak Checker Service")


AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth-service")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


LEAKED_PATH = os.path.join(
    BASE_DIR,
    "..",
    "infra",
    "json",
    "leaked_passwords.json"
)


class PasswordRequest(BaseModel):
    password: str


with open(LEAKED_PATH, "r", encoding="utf-8") as f:
    leaked_passwords = json.load(f)


def decode_token_return_username(
        token: str, timeout: float = 3.0
        ) -> Optional[str]:

    if not token:
        return None

    try:

        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(
            f"{AUTH_SERVICE_URL}/users/me", headers=headers, timeout=timeout
        )

        if resp.status_code == 200:
            body = resp.json()

            return body.get("username")
        else:

            return None

    except requests.RequestException:

        return None


@app.post("/check-password")
def check_password(
    request: PasswordRequest, token: str = Depends(oauth2_scheme)
):

    username = decode_token_return_username(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token")

    sha1 = hashlib.sha1(request.password.encode("utf-8")).hexdigest().upper()
    times = leaked_passwords.get(sha1, 0)

    return {"leaked": times > 0, "times": times}


@app.get("/health")
def health_check():
    return {"status": "ok"}
