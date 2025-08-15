from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.auth import (
    authenticate_user,
    create_access_token,
    decode_token_return_username,
)
from src.database import SessionLocal
from src.models import User
from src.schemas import UserCreate, UserOut
from src.utils import get_password_hash, send_email
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from src.logger import logger
from uuid import uuid4
from prometheus_fastapi_instrumentator import Instrumentator
import secrets


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def generate_verification_token():
    return secrets.token_urlsafe(32)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid4())
    logger_ctx = logger.bind(
        request_id=request_id,
        client_ip=request.client.host,
        method=request.method,
        path=request.url.path,
    )

    logger_ctx.info("Start request")
    response = await call_next(request)
    logger_ctx.info("End request", status_code=response.status_code)

    response.headers["X-Request-ID"] = request_id
    return response


async def get_db():
    async with SessionLocal() as session:
        yield session


@app.post("/register", status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.username == user.username)
    )
    user_db = result.scalars().first()
    if user_db:
        raise HTTPException(
            status_code=400, detail="Username already registered"
        )

    result = await db.execute(select(User).where(User.email == user.email))
    email_db = result.scalars().first()
    if email_db:
        raise HTTPException(
            status_code=400, detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    token = generate_verification_token()

    new_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        verification_token=token,
        is_verified=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    verification_link = f"https://app.com/verify-email?token={token}"
    body = (
    f"Hello {user.username},\n\n"
    f"Click this link to verify your email address:\n"
    f"{verification_link}"
    )
    send_email(user.email, "Validate your email address", body)

    return {"msg": "User registered successfully"}


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )


@app.get("/verify-email")
async def verify_email(
    token: str = Query(...), db: AsyncSession = Depends(get_db)
    ):
    result = await db.execute(
        select(User).where(User.verification_token == token)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=400, detail="Invalid verification token"
        )

    user.is_verified = True
    user.verification_token = None
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"msg": "Email verified successfully"}


@limiter.limit("5/minute")
@app.post("/token")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserOut)
async def read_users_me(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    username = decode_token_return_username(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=
            "Invalid or expired token"
        )
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@app.get("/health")
def health_check():
    return {"status": "ok"}


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
