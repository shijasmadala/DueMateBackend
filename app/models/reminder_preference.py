from datetime import time
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReminderChannel


class ReminderPreference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """When and how to remind a user about one payment item or one document."""

    __tablename__ = "reminder_preferences"
    __table_args__ = (
        CheckConstraint(
            "(payment_item_id IS NOT NULL AND document_id IS NULL) OR "
            "(payment_item_id IS NULL AND document_id IS NOT NULL)",
            name="exactly_one_target",
        ),
        CheckConstraint("days_before >= 0", name="days_before_non_negative"),
        CheckConstraint("channel IN ('push')", name="channel_valid"),
        UniqueConstraint(
            "payment_item_id",
            "days_before",
            "channel",
            name="uq_reminder_preferences_item_offset_channel",
        ),
        UniqueConstraint(
            "document_id",
            "days_before",
            "channel",
            name="uq_reminder_preferences_document_offset_channel",
        ),
        Index("ix_reminder_preferences_user_id_enabled", "user_id", "is_enabled"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_item_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("payment_items.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    days_before: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    remind_at: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        server_default=text("'09:00:00'"),
    )
    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=ReminderChannel.PUSH.value,
    )
    is_enabled: Mapped[bool] = mapped_column(
        nullable=False,
        server_default=text("true"),
    )

    user: Mapped["User"] = relationship(back_populates="reminder_preferences")
    payment_item: Mapped["PaymentItem | None"] = relationship(
        back_populates="reminder_preferences"
    )
    document: Mapped["Document | None"] = relationship(
        back_populates="reminder_preferences"
    )
    reminder_deliveries: Mapped[list["ReminderDelivery"]] = relationship(
        back_populates="reminder_preference"
    )
