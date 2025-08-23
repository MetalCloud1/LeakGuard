# -----------------------------------------------------------------------------
# Template created by Gilbert Ramirez GitHub: https://github.com/MetalCloud1
# Licensed under CC BY-NC-ND (custom) – see LICENSE.md for details
# You may view, study, and modify this template.
# Substantial modifications that add new functionality or transform the project
# may be used as your own work, as long as the original template is properly
# acknowledged.
# -----------------------------------------------------------------------------
from sqlalchemy import Column, String, Boolean
from src.database import Base


class User(Base):

    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    verification_token = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
