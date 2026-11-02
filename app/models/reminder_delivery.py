from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReminderDeliveryStatus


class ReminderDelivery(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One scheduled or sent reminder for a specific due/expiry occurrence."""

    __tablename__ = "reminder_deliveries"
    __table_args__ = (
        CheckConstraint(
            "(payment_item_id IS NOT NULL AND document_id IS NULL) OR "
            "(payment_item_id IS NULL AND document_id IS NOT NULL)",
            name="exactly_one_target",
        ),
        CheckConstraint(
            "status IN ('pending', 'sent', 'failed', 'cancelled')",
            name="status_valid",
        ),
        UniqueConstraint(
            "reminder_preference_id",
            "target_event_date",
            name="uq_reminder_deliveries_preference_event",
        ),
        Index(
            "ix_reminder_deliveries_status_scheduled_for",
            "status",
            "scheduled_for",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reminder_preference_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "reminder_preferences.id",
            ondelete="CASCADE",
            name="fk_reminder_deliveries_pref_id",
        ),
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
    target_event_date: Mapped[date] = mapped_column(Date, nullable=False)
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=ReminderDeliveryStatus.PENDING.value,
    )
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship(back_populates="reminder_deliveries")
    reminder_preference: Mapped["ReminderPreference"] = relationship(
        back_populates="reminder_deliveries"
    )
    payment_item: Mapped["PaymentItem | None"] = relationship(
        back_populates="reminder_deliveries"
    )
    document: Mapped["Document | None"] = relationship(
        back_populates="reminder_deliveries"
    )
