from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Account that owns every other row in the database."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, server_default="UTC")

    payment_items: Mapped[list["PaymentItem"]] = relationship(back_populates="user")
    documents: Mapped[list["Document"]] = relationship(back_populates="user")
    payment_records: Mapped[list["PaymentRecord"]] = relationship(back_populates="user")
    reminder_preferences: Mapped[list["ReminderPreference"]] = relationship(
        back_populates="user"
    )
    device_tokens: Mapped[list["DeviceToken"]] = relationship(back_populates="user")
    reminder_deliveries: Mapped[list["ReminderDelivery"]] = relationship(
        back_populates="user"
    )
