import enum

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

class UserRole(str, enum.Enum):
    admin = "admin"
    # crew role added phase 2

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    name: Mapped[str]
    phone: Mapped[str | None]
    active: Mapped[bool] = mapped_column(default=True)
