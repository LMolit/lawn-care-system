from geoalchemy2 import Geography
from sqlalchemy  import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

class Property(Base, TimestampMixin):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), index=True)
    address: Mapped[str]
    location: Mapped[str] = mapped_column(Geography(geometry_type="POINT", srid=4326))
    lawn_size_sqft: Mapped[int | None]
    access_notes: Mapped[str | None]
