from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import hashlib
import os
import requests
from typing import Optional

app = FastAPI(title="Password Leak Checker Service")

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth-service")
USE_HIBP = os.environ.get("USE_HIBP", "true").lower() == "true"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class PasswordRequest(BaseModel):
    password: str


def decode_token_return_username(
    token: str, timeout: float = 3.0
) -> Optional[str]:
    if not token:
        return None

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{AUTH_SERVICE_URL}/users/me", headers=headers, timeout=timeout
        )
        if response.status_code == 200:
            return response.json().get("username")
        return None

    except requests.RequestException:
        return None


def check_password_hibp(password: str) -> int:
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"HIBP API error: {exc}"
        )

    for line in response.text.splitlines():
        hash_tail, count = line.split(":")
        if hash_tail == suffix:
            return int(count)
    return 0


@app.post("/check-password")
def check_password(
    request: PasswordRequest, token: str = Depends(oauth2_scheme)
):
    username = decode_token_return_username(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    if USE_HIBP:
        times = check_password_hibp(request.password)
    else:
        times = 0

    return {"leaked": times > 0, "times": times}


@app.get("/health")
def health_check():
    return {"status": "ok"}
