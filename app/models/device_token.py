from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DevicePlatform


class DeviceToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A mobile device registered to receive push notifications for one user."""

    __tablename__ = "device_tokens"
    __table_args__ = (
        CheckConstraint("platform IN ('android', 'ios')", name="platform_valid"),
        UniqueConstraint("user_id", "token", name="uq_device_tokens_user_id_token"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token: Mapped[str] = mapped_column(String(512), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        server_default=text("true"),
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="device_tokens")

    def typed_platform(self) -> DevicePlatform:
        return DevicePlatform(self.platform)
