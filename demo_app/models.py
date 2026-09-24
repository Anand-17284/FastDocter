from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    customer_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )