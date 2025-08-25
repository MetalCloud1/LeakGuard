from setuptools import setup

setup(
    name="auth_service",
    version="0.1.0",
    description="Authentication microservice",
    author="Gilbert Ramirez",
    packages=["src"],  # directamente el paquete
    package_dir={"src": "src"},
    include_package_data=True,
    install_requires=[
        "fastapi>=0.100.0",
        "sqlalchemy>=2.0.0",
        "asyncpg>=0.27.0",
        "passlib[bcrypt]>=1.7.4",
        "python-jose>=3.3.0",
        "boto3>=1.26.0",
        "uvicorn>=0.22.0",
        "loguru>=0.7.0",
        "pydantic>=2.5.0",
        "slowapi>=0.1.5",
        "prometheus-fastapi-instrumentator>=6.0.1",
    ],
    python_requires=">=3.11",
)
